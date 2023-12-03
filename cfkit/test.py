from typing import Any
from threading import Thread

# Third-Party Imports
from pynput.keyboard import Controller, Key
from questionary import select as questSelect
from questionary import confirm as questConfirm
from cfkit.util.common import confirm, select_option
from time import sleep
def input_with_time_limit(
    func,
    timeout_seconds: float,
    default: Any = True,
    default_keys: str = 'y',
    **kwargs
  ) -> Any:
  """
  Documentation
  """
  # Create a thread for the question
  confirmation_thread = Thread(
    target = lambda: setattr(confirmation_thread, 'result', func(**kwargs))
  )
  # Start the thread
  confirmation_thread.start()
  # Wait for the thread to complete or for the timeout to occur
  confirmation_thread.join(timeout=timeout_seconds)

  if confirmation_thread.is_alive():
    # If the thread is still running, it means the timeout occurred
    keyboard = Controller()
    keyboard.press(default_keys)
    keyboard.release(default_keys)
    sleep(0.3)
    return default

  return confirmation_thread.result

# print(input_with_time_limit(select_option, 3, message="Confirm", data=["Youssra", "Khadija", "Ayet"], default="Youssra", default_keys=Key.enter))
print(input_with_time_limit(confirm, 3, message="Confirm"))

