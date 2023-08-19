#include <python.h>

int main() {
    Py_Initialize();  // Initialize the Python interpreter

    // Run a Python script
    FILE* file = fopen("your_script.py", "r");
    if (file) {
        PyRun_SimpleFile(file, "your_script.py");
        fclose(file);
    } else {
        PyErr_Print();
    }

    Py_Finalize();  // Finalize the Python interpreter
    return 0;
}
