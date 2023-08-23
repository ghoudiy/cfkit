package main

import (
  "bufio"
  "bytes"
  "fmt"
  "unicode"
  "io"
  "os"
  "os/exec"
  "strconv"
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

func print_error(err error) {
  if err != nil {
    fmt.Println("Error:", err)
    os.Exit(0)
  }
}

func createFile(file_name string) *os.File{
  file, err := os.Create(file_name)
  print_error(err)
  return file
}

func judge(command, memory_time_path, input_file, output_file, sampleID string, memory_limit float64) error {
  input, err := os.Open(input_file)
  print_error(err)
  output := createFile(output_file)
  memory_time_file := createFile(memory_time_path)

  write_errors_to_files := func(error_output bytes.Buffer) {

    _, err = fmt.Fprint(memory_time_file, "Runtime error on ", sampleID)
    print_error(err)
    _, err = fmt.Fprint(output, plain(error_output.Bytes()))
    print_error(err)
    os.Exit(0)
  }

  var e bytes.Buffer
  exec_errors := io.Writer(&e)

  cmds := splitCmd(command)
  
  cmd := exec.Command(cmds[0], cmds[1:]...)
  cmd.Stdin = input
  cmd.Stdout = output
  cmd.Stderr = exec_errors

  if err := cmd.Start(); err != nil {
    fmt.Println("I made an error 1")
    fmt.Println(err.Error())
    write_errors_to_files(e)
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
        fmt.Println("I made an error 2")
        fmt.Println(err.Error())
        write_errors_to_files(e)
      }
      running = false
    default:
      p, err := process.NewProcess(pid)
      if err == nil {
        m, err := p.MemoryInfo()
        if err == nil && m.RSS > maxMemory {
          maxMemory = m.RSS
        }
        if float64(maxMemory) > memory_limit {
          fmt.Fprint(memory_time_file, "Memory limit exceeded on ", sampleID)
        }
      }
    }
  }

  parseMemory := func(memory uint64) string {
    if memory > 1048576 {
      return fmt.Sprintf("%.3f MB", float64(memory)/1024.0/1024.0)
    } else if memory > 1024 {
      return fmt.Sprintf("%.3f KB", float64(memory)/1024.0)
    }
    return fmt.Sprintf("%v B", memory)
  }
  
  _, err = fmt.Fprint(memory_time_file, cmd.ProcessState.UserTime().Seconds() * 1000, " ms\n", parseMemory(maxMemory))
  print_error(err)
  return nil
}

func main() {
  L := os.Args[1:]
  if len(L) > 1 {
    execution_command := L[0]
    memoryLimit, err := strconv.ParseFloat(L[1], 64)
    if err != nil {
      fmt.Printf("Error parsing float: %v\n", err)
    }
    memory_time_path := L[2]
    in_path := L[3]
    out_path := L[4]
    sample_id := L[5]

    if len(L) == 7 {
      command_args := splitCmd(L[6])

      var e bytes.Buffer
      exec_errors := io.Writer(&e)

      cmd := exec.Command(command_args[0], command_args[1:]...)
      cmd.Stderr = exec_errors

      if err := cmd.Run(); err != nil {
        memory_time_file := createFile(memory_time_path)
        output := createFile(out_path)
        _, err = memory_time_file.WriteString("Compilation error")
        print_error(err)
        _, err = output.WriteString(plain(e.Bytes()))
        print_error(err)
        os.Exit(0)
      }
      os.Exit(1)
    }
    judge(execution_command, memory_time_path, in_path, out_path, sample_id, memoryLimit)
  }
}
// go run test.go ./output_cpp_three.out memory_cpp_three.txt in output_cpp_thee.txt "test 1" "g++ -o output_cpp_three.out dislike_of_three.cc"
// go run test.go ./hello.out 512000000 memory_hello.txt in hello_output.out "test 1" "g++ -Wall -Wextra -Wconversion -static -fno-strict-aliasing -pedantic -Wshadow -Wfloat-equal -Wlogical-op -Wformat=2 -Wshift-overflow=2 -Wduplicated-cond -fsanitize=undefined -fno-sanitize-recover -fstack-protector -O2 -std=c++20 -o hello.out code.cpp"
// go run test.go ./output_cpp.out memory_cpp.txt in output_cpp.txt "test 1" "g++ -o output_cpp.out cpp_make_error.cpp"
// go run test.go "python3 py_make_error.py" memory_test_python.txt in_dislike_of_three python_test_memory.txt "test 1"