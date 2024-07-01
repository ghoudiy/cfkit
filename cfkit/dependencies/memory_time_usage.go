package main
// Part of this code is derived from cf-tool
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

func print_error(err error, err_num int) {
  if err != nil {
    fmt.Println("Go Error", err_num, ":", err)
    os.Exit(1)
  }
}

func createFile(file_name string) *os.File{
  file, err := os.Create(file_name)
  print_error(err, 2)
  return file
}

func judge(command, memory_time_path, input_file, output_file string) error {
  input, err := os.Open(input_file)
  print_error(err, 1)
  output := createFile(output_file)
  memory_time_file := createFile(memory_time_path)

  parseMemory := func(memory uint64) string {
    if memory > 1048576 {
      return fmt.Sprintf("%.3f MB", float64(memory)/1024.0/1024.0)
    } else if memory > 1024 {
      return fmt.Sprintf("%.3f KB", float64(memory)/1024.0)
    }
    return fmt.Sprintf("%v B", memory)
  }

  write_errors_to_files := func(error_output bytes.Buffer, time_memory_str string, err_num int) {

    _, err = fmt.Fprint(memory_time_file, time_memory_str + plain(error_output.Bytes()))
    print_error(err, err_num)
    os.Exit(1)
  }


  var e bytes.Buffer
  exec_errors := io.Writer(&e)

  cmds := splitCmd(command)

  cmd := exec.Command(cmds[0], cmds[1:]...)
  cmd.Stdin = input
  cmd.Stdout = output
  cmd.Stderr = exec_errors

  if err := cmd.Start(); err != nil {
    write_errors_to_files(e, "Time:   0 ms\nMemory: 0 B\n", 3)
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
        p, err := process.NewProcess(pid)
        m, err := p.MemoryInfo() // Return memory in bytes

        if err == nil && m.RSS > maxMemory {
          maxMemory = m.RSS
        }
        write_errors_to_files(e, fmt.Sprintf("Time:   %f ms\nMemory: %s\n", cmd.ProcessState.UserTime().Seconds() * 1000, parseMemory(maxMemory)), 4)
      }
      running = false
    default:
      p, err := process.NewProcess(pid)
      m, err := p.MemoryInfo()

      if err == nil && m.RSS > maxMemory {
        maxMemory = m.RSS
      }
    }
  }

  cmd.Wait()
  _, err = fmt.Fprint(memory_time_file, fmt.Sprintf("Time:   %f ms\nMemory: %s\n", cmd.ProcessState.UserTime().Seconds() * 1000, parseMemory(maxMemory)))
  print_error(err, 5)
  return nil
}

func main() {
  L := os.Args[1:]
  execution_command := L[0]
  memory_time_path := L[1]
  in_path := L[2]
  participant_output_path := L[3]

  judge(execution_command, memory_time_path, in_path, participant_output_path)
}
