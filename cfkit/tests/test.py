# from prompt_toolkit import print_formatted_text, HTML
# from prompt_toolkit.styles import Style
# from prompt_toolkit.formatted_text import to_plain_text, to_formatted_text
# from prompt_toolkit import prompt
# from cfkit.utils.variables import color_conf
# from cfkit.utils.input import select_option
# from cfkit.utils.print import colored_text

# style = Style([(key, value) for key, value in color_conf["theme"].items()])
# try:
#   try:
#     raise InterruptedError(["wrong answer", "error 4", "hello"])
#   except InterruptedError as err:
#     if True:
#       raise InterruptedError(err)
# except InterruptedError as err2:
#   print(err2.args[0], "I am here")

class example:
  def __init__(self) -> None:
    # self.temparature = None
    pass

  @property
  def name(self):
    print("I am inside name property")
    return "yassine"
  
print(example().name)
print(example().name + "ghoudi")


# class Date:
#     def __init__(self, year, month, day):
#         print("HEllo")
#         self.year = year
#         self.month = month
#         self.day = day

#     @classmethod
#     def from_string(cls, date_string):
#         year, month, day = map(int, date_string.split('-'))
#         return cls(year, month, day)

# # Using the factory method
# date = Date.from_string("2023-07-04")
# print(date.year, date.month, date.day)  # Output: 2023 7 4

