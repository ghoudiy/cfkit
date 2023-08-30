from mechanicalsoup import StatefulBrowser
from re import search

def codeforces_login(problem_code, programming_language, path):
    # Check if login was successful
    browser = StatefulBrowser()
    exit()
    form_url = f'https://codeforces.com/contest/{search(r"[A-z]", problem_code).start()}/submit'
    browser.open(form_url)
    form = browser.select_form(f'form[class="submit-form"]')

    # Fill out the form fields
    form.set("submittedProblemCode", problem_code)
    form.set("programTypeId", programming_language)
    form.set("sourceFile", open(path, "rb"))

    # Submit the form
    browser.submit_selected()

    # Check if the submission was successful (You may need to implement additional script depending on the response)
    pass


if __name__ == "__main__":
    codeforces_login("144A", "31", "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/144A_Arrival_of_the_General.py")
