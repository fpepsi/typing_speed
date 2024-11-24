import os
import customtkinter as ctk
from customtkinter import CTkTextbox, CTkEntry, CTkButton
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from unidecode import unidecode
import requests
from dotenv import load_dotenv
import json
from random import randint


load_dotenv()
NEWS = "breaking"
news_api_key = os.environ.get("NEWS_API_KEY")
newsapi_url = "https://newsapi.org/v2/top-headlines"
# newsapi_url = "https://newsapi.org/v2/everything"
parameters_newsapi = {
        # "q": NEWS,
        "pageSize": 50,
        "country": "US",
        "category": "science",
        # "language": "en",
        # "sortBy": "relevancy",
        "apiKey": news_api_key,
}

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Light", "Dark"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

TEST_TIME = 1 # minutes

class TypingSpeedTest(tk.Tk):
    def __init__(self):
        """
        This app fetches a random news article and uses it as a sample for the user, who needs to
        type it as fast and accurately as possible
        """
        super().__init__()
        self.title("Typing Test")
        self.geometry("800x400")

        # Create variables for checkboxes
        self.time_var = tk.IntVar(value=1)          # check box variable selecting timed-type test
        self.full_text_var = tk.IntVar(value=0)     # check box variable selecting full-text-type test
        # initialize variable values
        self.initialize_vars()
        self.get_news()


        ### App GUI screen using custom tkinter
        # create app container
        self.container = ctk.CTkFrame(self, bg_color='white')
        self.container.pack(expand=True, fill='both')

        # top labels frame
        self.top_frame = ctk.CTkFrame(master=self.container)
        self.top_frame.pack(expand=True, fill='both')

        # left labels frame
        self.left_frame = ctk.CTkFrame(master=self.top_frame)
        self.left_frame.pack(side='left', expand=True, fill='both')

        # Label to display timer
        self.timer_label = tk.Label(self.left_frame, text=f"Time remaining: --:--", font=("Helvetica", 20), state='normal', width=30)
        self.timer_label.pack( padx=10, pady=10, expand=True)

        # Label to display words to finish
        self.words_togo_label = tk.Label(self.left_frame, text=f"Words remaining: ----", font=("Helvetica", 20), state='disabled', width=30)
        self.words_togo_label.pack(padx=10, pady=10, expand=True)
        self.words_togo_label.pack_forget() # initiatially invisible

        # Label to display words per minute
        self.words_permin_label = tk.Label(self.left_frame, text="Words per minute: ---", font=("Helvetica", 20),
                                         state='normal', width=30)
        self.words_permin_label.pack(padx=10, pady=10, expand=True)

        # right labels frame
        self.right_frame = ctk.CTkFrame(master=self.top_frame)
        self.right_frame.pack(side='left', expand=True, fill='both')

        # Label to display characters per minute
        self.chars_permin_label = tk.Label(self.right_frame, text="Characters per minute: ----", font=("Helvetica", 20),
                                         state='normal', width=30)
        self.chars_permin_label.pack(padx=10, pady=10, expand=True)

        # Label to display % wrong words
        self.incorrect_pct_label = tk.Label(self.right_frame, text="Errors: --%", font=("Helvetica", 20),
                                            state='normal', width=30)
        self.incorrect_pct_label.pack(padx=10, pady=10, expand=True)

        # checkbox frame
        self.checkbox_frame = ctk.CTkFrame(master=self.container)
        self.checkbox_frame.pack(expand=True, fill='y')
        self.checkbox_frame.grid_columnconfigure((0,1), weight=1, uniform='a')
        self.checkbox_frame.grid_rowconfigure(index=0, weight=1)

        # Configure a custom style for checkbuttons
        style = ttk.Style()
        style.configure(
            "Custom.TCheckbutton",
            font=("Helvetica", 20),
            padding=5,
            anchor = 'center'
        )

        # checkbuttons to choose test type (timed or full-text)
        self.time_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Time",
            width=30,
            style="Custom.TCheckbutton",
            variable=self.time_var,
            state='normal',
            command=self.toggle_time
        )
        self.time_checkbox.grid(column=0, row=0, padx=20)

        self.full_text_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Full Text",
            width=30,
            style="Custom.TCheckbutton",
            variable=self.full_text_var,
            state='disabled',
            command=self.toggle_full_text
        )
        self.full_text_checkbox.grid(column=1, row=0, padx=20)

        # Create CTkTextbox
        self.sample_text_view = CTkTextbox(
            self.container,
            width=700,
            height=100,
            wrap="word",
            font=("Helvetica", 20),
            fg_color="white",  # Background color
            text_color="black",  # Text color
            border_width=2,  # Optional border width
            corner_radius=10  # Rounded corners
        )
        self.sample_text_view.pack(padx=10, pady=10)

        # Set up tags for styling
        self.sample_text_view.tag_config("green_bg", background="green")  # used to highlight current word
        self.sample_text_view.tag_config("red",
                                         foreground="red")  # used on current word's character and past words, if wrong
        self.sample_text_view.tag_config("white",
                                         foreground="white")  # used on current word character, if matches original
        self.sample_text_view.tag_config("green", foreground="green")  # used on past words, if correct

        # displays placeholder message before user starts test
        placeholder = "Your text message will be displayed here..."
        self.sample_text_view.insert("0.0", placeholder)

        # Disable editing on sample test screen
        self.sample_text_view.configure(state="disabled")

        # Create a CTkTextbox widget to capture text
        placeholder = "Type here..."
        self.user_text_entry = CTkEntry(master=self.container,
                                width=700,
                                height=40,
                                corner_radius=10,
                                border_width=2,
                                fg_color="light gray",
                                border_color="blue",
                                text_color="black",
                                placeholder_text=placeholder,
                                font=("Helvetica", 20),
                                justify="center",
                                  )
        self.user_text_entry.pack(padx=10, pady=10)

        # Initially disables editing until test starts
        self.user_text_entry.configure(state="disabled")

        # buttons frame
        self.buttons_frame = ctk.CTkFrame(master=self.container)
        self.buttons_frame.pack(expand=True, fill='y')
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1, uniform='a')
        self.buttons_frame.grid_rowconfigure(index=0, weight=1)

        # start test button
        self.start_button = CTkButton(master=self.buttons_frame,
                                      width=140,
                                      height=28,
                                      text='Start Test',
                                      text_color='white',
                                      font=("Helvetica", 20),
                                      command=lambda: self.start_test(),
                                      )
        self.start_button.grid(column=0, row=0, padx=20)

        # quit test button
        self.quit_button = CTkButton(master=self.buttons_frame,
                                      width=140,
                                      height=28,
                                      text='Quit',
                                      text_color='white',
                                      font=("Helvetica", 20),
                                      command=lambda: self.quit(),
                                      )
        self.quit_button.grid(column=1, row=0, padx=20)

    ### App GUI functionality

    def initialize_vars(self):
        self.user_text = ''  # string chain containing user typed text
        self.sample_text = ''  # string chain with the text words that should be typed by user
        self.word_index = 0  # counts the sample_text words sequentially
        self.col_index = 0  # counts the characters positions to apply tagging
        self.line_index = 1  # tracks the line of the highlighted word; used only for scrolling
        # app screen labels
        self.words_per_min = 0.0  # calculates average word typing speed
        self.chars_per_min = 0.0  # calculates average character typing speed
        self.words_to_go = 0
        self.sample_text_list = []  # this list will be compared to user_text_list for word mismatch
        self.error_percent = 0.0  # calculates percent of typing inaccuracies
        self.start_time = None      # initiates the test's time control
        self.test_is_off = True
        self.refresh = None
        self.time_limit = timedelta(minutes=TEST_TIME) # Set time limit for the test


    def toggle_time(self):
        """Manages labels states when time-test option is selected"""
        if self.time_var.get() == 1:
            self.words_togo_label.pack_forget()
            self.timer_label.pack(before=self.words_permin_label, padx=10, pady=10, expand=True)
            self.timer_label.config(state='normal')
            self.full_text_checkbox.config(state="disabled")
            self.start_button.configure(state='normal')
        else:
            self.full_text_checkbox.config(state="normal")
            self.start_button.configure(state='disabled')


    def toggle_full_text(self):
        """Manages labels states when full-tes-text option is selected"""
        if self.full_text_var.get() == 1:
            self.timer_label.pack_forget()
            self.words_togo_label.pack(before=self.words_permin_label, padx=10, pady=10, expand=True)
            self.words_togo_label.config(state='normal')
            self.time_checkbox.config(state="disabled")
            self.start_button.configure(state='normal')
        else:
            self.time_checkbox.config(state="normal")
            self.start_button.configure(state='disabled')


    def start_test(self):
        '''Initiates the test processes '''
        # modifies test input to a standard format consisting of one word or character followed by one space
        self.get_sample_text()
        # sets up user focus and allows typing
        self.user_text_entry.configure(state="normal")
        self.user_text_entry.delete(0, ctk.END)  # Delete placeholder text
        self.user_text_entry.focus_set()
        self.user_text_entry.bind('<KeyRelease>', self.compare_texts)
        # fetches new text and display it to user
        self.sample_text_view.configure(state="normal")  # Allow editing for styling
        self.sample_text_view.delete('0.0', 'end')  # Delete placeholder text
        self.sample_text_view.insert('0.0', self.sample_text)
        self.update_sample_text_view()
        self.sample_text_view.configure(state="disabled")
        self.time_checkbox.config(state='disabled')
        self.full_text_checkbox.config(state='disabled')
        # starts timer management
        self.start_timer()


    def get_sample_text(self):
        '''reorganizes sample_text string to ensure there are only ascII chars and single spaces between words'''
        sample_text = self.get_news()
        temp_list = list(sample_text.strip().split())
        self.sample_text_list = [unidecode(item) for item in temp_list if item != ' ']
        self.words_to_go = len(self.sample_text_list)
        for item in self.sample_text_list:
            new_word = item + ' '
            self.sample_text += new_word


    def start_timer(self):
        """Starts and manages the timer."""
        if self.test_is_off:
            self.start_time = datetime.now()
            self.test_is_off = False
            self.update_labels()


    def update_labels(self):
        ''' calculates the variables used to populate the labels'''
        if self.refresh:
            self.after_cancel(self.refresh)
        self.elapsed_time = datetime.now() - self.start_time
        self.remaining_time = self.time_limit - self.elapsed_time
        # calculates test metrics
        char_count = 0
        wrong_word_count = 0
        user_text_words = list(self.user_text.strip().split(' '))
        for index, item in enumerate(user_text_words):
            if index < len(self.sample_text_list):
                char_count += len(item)
                if item != self.sample_text_list[index]:
                    wrong_word_count += 1
            else:
                break
        self.error_percent = wrong_word_count / len(user_text_words)
        self.words_to_go = len(self.sample_text_list) - len(user_text_words)
        if self.elapsed_time.seconds > 0:
            self.words_per_min = int(len(user_text_words) / (self.elapsed_time.seconds / 60))
            self.chars_per_min = int(char_count / (self.elapsed_time.seconds / 60))
        # update screens and labels accordingly
        self.timer_label.config(text=f"Time remaining: {self.remaining_time.seconds} seconds")
        self.words_permin_label.config(text=f'Words per minute: {self.words_per_min}')
        self.chars_permin_label.config(text=f'Characters per minute: {self.chars_per_min}')
        self.words_togo_label.config(text=f'Words remaining: {self.words_to_go}')
        self.incorrect_pct_label.config(text=f'Errors: {self.error_percent:.2%}')
        # will update the label every 0.1 seconds
        self.refresh = self.after(100, self.update_labels)

        # check if end of test
        if self.time_var.get() == 1 and self.remaining_time.seconds <= 0:
            self.timer_label.config(text="Time's up!")
            self.end_test()
        elif self.word_index == len(self.sample_text_list):
            self.end_test()


    def end_test(self):
        ''' resets app display and labels'''
        self.after_cancel(self.refresh)
        self.user_text_entry.delete(0, ctk.END)
        self.user_text_entry.configure(state="disabled")
        self.user_text_entry.unbind('<KeyRelease>')
        self.sample_text_view.configure(state="normal")
        self.sample_text_view.delete('0.0', 'end')  # Delete sample text
        self.sample_text_view.insert('0.0', f'Your text = {self.user_text}')  # display user text showing what was typed
        self.sample_text_view.configure(state="disabled")
        if self.full_text_var == 1:
            self.full_text_checkbox.config(state='normal')
        else:
            self.time_checkbox.config(state='normal')
        self.initialize_vars()


    def update_sample_text_view(self):
        '''highlights the current word to be typed and scrolls line up if end of line is reached'''
        # select sample_text word based on index
        sample_word = self.sample_text.split()[self.word_index]
        self.sample_text_view.tag_add('green_bg', f'1.{self.col_index}',
                                      f'1.{self.col_index + len(sample_word)}')
        highlight_tag_index = self.sample_text_view.tag_ranges('green_bg')[1]
        current_line_index = self.sample_text_view.dlineinfo(highlight_tag_index)[1]
        if current_line_index > self.line_index:
            self.sample_text_view.yview_scroll(1, "unit")


    def compare_texts(self, event):
        """Compares the characters in self.user_text with self.sample_text."""
        # the if statement below ignores function-keys events
        if event.char:
            # selects the next sample_text word and retrieves latest word typed by user
            sample_word = self.sample_text.split()[self.word_index]
            new_word = self.user_text_entry.get()

            # if there is user_text, evaluates if the last character is alphanumeric or space
            # also manages tagging for proper character's coloring
            if new_word:
                self.sample_text_view.configure(state="normal")
                new_char = list(new_word)[-1]
                if new_char.isalnum():
                    # this loop tags the latest sample_text word's letters according to matching user_text's
                    for tag in self.sample_text_view.tag_names():
                        if tag != 'green_bg':
                            self.sample_text_view.tag_remove(tag, f'1.{self.col_index}',
                                                             f'1.{self.col_index + len(sample_word)}')
                    # applies whate tag to matching characters, otherwise applies red tag
                    char_index = 0
                    for char1, char2 in zip(sample_word, new_word): # compares user and sample words and sets char tags
                        if char1 == char2:
                            tag = 'white'
                        else:
                            tag = 'red'
                        self.sample_text_view.tag_add(tag, f'1.{self.col_index + char_index}',
                                                      f'1.{self.col_index + char_index + 1}')
                        char_index += 1
                # when space is typed, app considers that user moves to next word
                # last sample_text word will be tagged green (correct) or red (wrong)
                # user word will be added to user_text string and tag indexes rolled forward to next word
                elif new_char.isspace():
                    for tag in self.sample_text_view.tag_names():
                        self.sample_text_view.tag_remove(tag, f'1.{self.col_index}',
                                                         f'1.{self.col_index + len(sample_word)}')
                    if new_word.strip() != sample_word:
                        self.sample_text_view.tag_add('red', f'1.{self.col_index}',
                                                      f'1.{self.col_index + len(sample_word)}')
                    else:
                        self.sample_text_view.tag_add('green', f'1.{self.col_index}',
                                                      f'1.{self.col_index + len(sample_word)}')
                    self.user_text += new_word.strip() + ' '
                    self.user_text_entry.delete(0, ctk.END)
                    self.word_index += 1  # self.word_index moves to next word
                    self.col_index += len(sample_word) + 1  # self.col_index moves to next sample_text word
                    if self.word_index < len(self.sample_text_list):
                        self.update_sample_text_view()
                self.sample_text_view.configure(state="disabled")  # disallow editing for styling
            else:
                pass


    def quit(self):
        self.destroy()


    def get_news(self):
        file_name = "news_file.json"
        try:
            with open(file_name) as file:
                newsapi = json.load(file)
        except FileNotFoundError:
            response = requests.get(newsapi_url, params=parameters_newsapi)
            response.raise_for_status()
            newsapi = response.json()
            with open(file_name, "w") as file:
                json.dump(newsapi, file)
        large_size = True
        while large_size:
            random_art = randint(0, len(newsapi['articles']) - 1)
            article = newsapi['articles'][random_art]['content']
            if len(list(article.split(' '))) <= 600:
                large_size = False
        return article

# Run the app
if __name__ == '__main__':
    app = TypingSpeedTest()
    app.mainloop()
