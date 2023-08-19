package main

import (
  "bufio"
  "bytes"
  "fmt"
  "unicode"
  "io"
  "os"
  "os/exec"
  "github.com/shirou/gopsutil/process"

)
func splitCmd(s string) (res []string) {
  var buf bytes.Buffer
  insideQuotes := false
  for _, r := range s {
    switch {
    case unicode.IsSpace(r) && !insideQuotes:
      if buf.Len() > 0 {
        res = append(res, buf.String())
        buf.Reset()
      }
    case r == '"' || r == '\'':
      if insideQuotes {
        res = append(res, buf.String())
        buf.Reset()
        insideQuotes = false
        continue
      }
      insideQuotes = true
    default:
      buf.WriteRune(r)
    }
  }
  if buf.Len() > 0 {
    res = append(res, buf.String())
  }
  return
}

func plain(raw []byte) string {
  buf := bufio.NewScanner(bytes.NewReader(raw))
  var b bytes.Buffer
  newline := []byte{'\n'}
  for buf.Scan() {
    b.Write(bytes.TrimSpace(buf.Bytes()))
    b.Write(newline)
  }
  return b.String()
}

func judge(command, memory_time_output, input_file, output_file, sampleID string) error {
  inPath := fmt.Sprintf(input_file)
  
  input, err := os.Open(inPath)
  if err != nil {
    return err
  }
  var o bytes.Buffer
  output := io.Writer(&o)
  
  cmds := splitCmd(command)

  cmd := exec.Command(cmds[0], cmds[1:]...)
  cmd.Stdin = input
  cmd.Stdout = output
  cmd.Stderr = os.Stderr
  if err := cmd.Start(); err != nil {
    return fmt.Errorf("Runtime Error %v:   %v", sampleID, err.Error())
  }

  pid := int32(cmd.Process.Pid)
  maxMemory := uint64(0)
  ch := make(chan error)
  go func() {
    ch <- cmd.Wait()
  }()
  
  running := true
  for running {
    select {
    case err := <-ch:
      if err != nil {
        return fmt.Errorf("Runtime Error %v:   %v", sampleID, err.Error())
      }
      running = false
    default:
      p, err := process.NewProcess(pid)
      if err == nil {
        m, err := p.MemoryInfo()
        if err == nil && m.RSS > maxMemory {
          maxMemory = m.RSS
        }
      }
    }
  }

  parseMemory := func(memory uint64) string {
    if memory > 1024*1024 {
      return fmt.Sprintf("%.3fMB", float64(memory)/1024.0/1024.0)
    } else if memory > 1024 {
      return fmt.Sprintf("%.3fKB", float64(memory)/1024.0)
    }
    return fmt.Sprintf("%vB", memory)
  }
   out := plain(o.Bytes())
   file, err := os.Create(output_file)
   if err != nil {
    fmt.Println("Error:", err)
    return nil
    }
    defer file.Close()
  
    _, err = file.WriteString(out)
    if err != nil {
      fmt.Println("Error:", err)
      return nil
    }
   
   file, err = os.Create(memory_time_output)
   if err != nil {
    fmt.Println("Error:", err)
    return nil
    }
    defer file.Close()
    aux := fmt.Sprintf("%f ms\n%v", cmd.ProcessState.UserTime().Seconds() * 1000, parseMemory(maxMemory))
    _, err = file.WriteString(aux)
    if err != nil {
      fmt.Println("Error:", err)
      return nil
    }
  return nil
}
func main() {
  L := os.Args[1:]
  if len(L) > 1 {
    execution_command := L[0]
    memory_time_output := L[1]
    in_path := L[2]
    out_path := L[3]
    sample_id := L[4]
    
    if len(L) == 6 {
      command_args := splitCmd(L[5])
      exec.Command(command_args[0], command_args[1:]...).Run()
     }
    judge(execution_command, memory_time_output, in_path, out_path, sample_id)
  }
}
