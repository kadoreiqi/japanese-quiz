import tkinter as tk
from tkinter import filedialog, messagebox
import random

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Japanese Quiz Application")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")
        
        self.questions = []
        self.current_question_idx = 0
        self.score = 0
        self.selected_answer = tk.IntVar()
        
        self.create_start_screen()
    
    def create_start_screen(self):
        """Create the initial screen with file selection"""
        self.clear_window()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = tk.Label(frame, text="Japanese Quiz Application", 
                              font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=20)
        
        instruction_label = tk.Label(frame, text="Select a question bank file to begin", 
                                    font=("Arial", 12), bg="#f0f0f0", fg="#666")
        instruction_label.pack(pady=10)
        
        select_btn = tk.Button(frame, text="Select Question Bank", 
                              command=self.load_questions, 
                              font=("Arial", 14), bg="#4CAF50", fg="white",
                              padx=20, pady=10, cursor="hand2")
        select_btn.pack(pady=20)
    
    def load_questions(self):
        """Open file dialog and load questions"""
        file_path = filedialog.askopenfilename(
            title="Select Question Bank File", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.questions = self.load_question_bank(file_path)
                self.questions = self.randomize_choices(self.questions)
                random.shuffle(self.questions)  # Shuffle question order
                
                if self.questions:
                    self.current_question_idx = 0
                    self.score = 0
                    self.create_quiz_screen()
                else:
                    messagebox.showerror("Error", "No questions found in the file!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
    
    def load_question_bank(self, file_path):
        """Load questions from file"""
        questions = []
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        question = None
        choices = []
        correct = None
        explanation = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("Q:"):
                if question:
                    questions.append({
                        "question": question,
                        "choices": choices,
                        "correct": correct,
                        "explanation": explanation
                    })
                question = line[2:].strip()
                choices = []
                correct = None
                explanation = None
            elif line.startswith("A:"):
                correct = len(choices)
                choices.append(line[2:].strip())
            elif line.startswith("B:") or line.startswith("C:"):
                choices.append(line[2:].strip())
            elif line.startswith("Explanation:"):
                explanation = line[12:].strip()
        
        if question:
            questions.append({
                "question": question,
                "choices": choices,
                "correct": correct,
                "explanation": explanation
            })
        
        return questions
    
    def randomize_choices(self, questions):
        """Randomize answer choices"""
        for question in questions:
            correct_answer = question["choices"][question["correct"]]
            random.shuffle(question["choices"])
            question["correct"] = question["choices"].index(correct_answer)
        return questions
    
    def create_quiz_screen(self):
        """Create the main quiz interface"""
        self.clear_window()
        
        # Header frame with progress info
        header_frame = tk.Frame(self.root, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        self.progress_label = tk.Label(header_frame, 
                                       text=f"Question {self.current_question_idx + 1} of {len(self.questions)}", 
                                       font=("Arial", 16, "bold"), bg="#2196F3", fg="white")
        self.progress_label.pack(pady=10)
        
        self.remaining_label = tk.Label(header_frame, 
                                       text=f"Remaining: {len(self.questions) - self.current_question_idx}", 
                                       font=("Arial", 12), bg="#2196F3", fg="white")
        self.remaining_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Question label
        question = self.questions[self.current_question_idx]
        self.question_label = tk.Label(content_frame, 
                                       text=question["question"], 
                                       font=("Arial", 16), 
                                       bg="#f0f0f0", 
                                       wraplength=600,
                                       justify="left")
        self.question_label.pack(pady=20)
        
        # Radio buttons for choices
        self.selected_answer.set(-1)
        self.radio_buttons = []
        
        for i, choice in enumerate(question["choices"]):
            rb = tk.Radiobutton(content_frame, 
                               text=choice, 
                               variable=self.selected_answer, 
                               value=i,
                               font=("Arial", 13),
                               bg="#f0f0f0",
                               activebackground="#f0f0f0",
                               padx=20,
                               pady=10,
                               wraplength=600,
                               justify="left")
            rb.pack(anchor="w", pady=5)
            self.radio_buttons.append(rb)
        
        # Submit button
        submit_btn = tk.Button(content_frame, 
                              text="Submit Answer", 
                              command=self.check_answer,
                              font=("Arial", 14, "bold"),
                              bg="#4CAF50",
                              fg="white",
                              padx=30,
                              pady=10,
                              cursor="hand2")
        submit_btn.pack(pady=30)
        
        # Score label
        self.score_label = tk.Label(content_frame, 
                                    text=f"Current Score: {self.score}/{self.current_question_idx}", 
                                    font=("Arial", 12),
                                    bg="#f0f0f0",
                                    fg="#666")
        self.score_label.pack()
    
    def check_answer(self):
        """Check the selected answer and move to next question"""
        if self.selected_answer.get() == -1:
            messagebox.showwarning("No Selection", "Please select an answer!")
            return
        
        question = self.questions[self.current_question_idx]
        user_answer = self.selected_answer.get()
        correct_answer = question["correct"]
        
        if user_answer == correct_answer:
            self.score += 1
            messagebox.showinfo("Correct! ✓", "That's the right answer!")
        else:
            messagebox.showerror("Incorrect ✗", 
                               f"The correct answer was:\n{question['choices'][correct_answer]}")
        
        # Show explanation after answering
        messagebox.showinfo("Explanation", question["explanation"])
        
        self.current_question_idx += 1
        
        if self.current_question_idx < len(self.questions):
            self.create_quiz_screen()
        else:
            self.show_results()
    
    def show_results(self):
        """Display final results"""
        self.clear_window()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = tk.Label(frame, text="Quiz Complete!", 
                              font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#4CAF50")
        title_label.pack(pady=20)
        
        percentage = (self.score / len(self.questions)) * 100
        score_label = tk.Label(frame, 
                              text=f"Your Score: {self.score}/{len(self.questions)}", 
                              font=("Arial", 20), bg="#f0f0f0", fg="#333")
        score_label.pack(pady=10)
        
        percentage_label = tk.Label(frame, 
                                   text=f"({percentage:.1f}%)", 
                                   font=("Arial", 16), bg="#f0f0f0", fg="#666")
        percentage_label.pack(pady=5)
        
        # Feedback based on score
        if percentage >= 90:
            feedback = "Excellent! 素晴らしい!"
        elif percentage >= 70:
            feedback = "Great job! よくできました!"
        elif percentage >= 50:
            feedback = "Good effort! 頑張りました!"
        else:
            feedback = "Keep practicing! もっと頑張って!"
        
        feedback_label = tk.Label(frame, text=feedback, 
                                 font=("Arial", 14, "italic"), bg="#f0f0f0", fg="#2196F3")
        feedback_label.pack(pady=20)
        
        # Restart button
        restart_btn = tk.Button(frame, text="Take Another Quiz", 
                               command=self.create_start_screen,
                               font=("Arial", 14), bg="#2196F3", fg="white",
                               padx=20, pady=10, cursor="hand2")
        restart_btn.pack(pady=10)
        
        exit_btn = tk.Button(frame, text="Exit", 
                            command=self.root.quit,
                            font=("Arial", 14), bg="#f44336", fg="white",
                            padx=20, pady=10, cursor="hand2")
        exit_btn.pack(pady=5)
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
