import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import json
import os
from pathlib import Path

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Japanese Quiz Application")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.questions = []
        self.current_batch_idx = 0
        self.batch_size = 10
        self.total_score = 0
        self.user_answers = {}
        self.progress_file = "quiz_progress.json"
        self.current_file_path = None
        self.seen_questions = set()  # Track questions seen in current session
        
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
        
        # Show progress info if available
        if os.path.exists(self.progress_file):
            info_label = tk.Label(frame, 
                                text="(Progress from previous sessions will be loaded)", 
                                font=("Arial", 10, "italic"), 
                                bg="#f0f0f0", fg="#999")
            info_label.pack(pady=5)
    
    def load_questions(self):
        """Open file dialog and load questions"""
        file_path = filedialog.askopenfilename(
            title="Select Question Bank File", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_file_path = file_path
                self.questions = self.load_question_bank(file_path)
                
                # Load progress for this specific file
                progress = self.load_progress()
                file_key = self.get_file_key(file_path)
                
                if file_key in progress:
                    file_progress = progress[file_key]
                    answered_indices = set(file_progress.get('answered', []))
                    
                    # Separate answered and unanswered questions
                    unanswered = [q for i, q in enumerate(self.questions) 
                                 if i not in answered_indices]
                    answered = [q for i, q in enumerate(self.questions) 
                               if i in answered_indices]
                    
                    if not unanswered:
                        # All questions answered - ask to restart
                        response = messagebox.askyesno(
                            "All Questions Completed",
                            f"You've completed all {len(self.questions)} questions!\n\n"
                            "Do you want to restart with all questions?"
                        )
                        if response:
                            self.reset_progress(file_key)
                            unanswered = self.questions.copy()
                            answered = []
                        else:
                            return
                    
                    # Randomize both groups
                    random.shuffle(unanswered)
                    random.shuffle(answered)
                    
                    # Prioritize unanswered questions
                    self.questions = unanswered + answered
                    
                    messagebox.showinfo(
                        "Progress Loaded",
                        f"Unanswered questions: {len(unanswered)}\n"
                        f"Previously answered: {len(answered)}\n\n"
                        f"Unanswered questions will be shown first."
                    )
                else:
                    # New file - just randomize
                    random.shuffle(self.questions)
                
                # Randomize choices for all questions
                self.questions = self.randomize_choices(self.questions)
                
                if self.questions:
                    self.current_batch_idx = 0
                    self.total_score = 0
                    self.user_answers = {}
                    self.seen_questions = set()
                    self.create_quiz_screen()
                else:
                    messagebox.showerror("Error", "No questions found in the file!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
    
    def get_file_key(self, file_path):
        """Generate a unique key for the file"""
        return os.path.basename(file_path)
    
    def load_progress(self):
        """Load progress from JSON file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_progress(self):
        """Save progress to JSON file"""
        if not self.current_file_path:
            return
        
        progress = self.load_progress()
        file_key = self.get_file_key(self.current_file_path)
        
        # Get original question texts to track which ones were answered
        original_questions = self.load_question_bank(self.current_file_path)
        
        # Find indices of questions answered in this session
        answered_indices = []
        for idx in self.seen_questions:
            if idx < len(original_questions):
                answered_indices.append(idx)
        
        # Merge with existing progress
        if file_key not in progress:
            progress[file_key] = {'answered': []}
        
        existing_answered = set(progress[file_key].get('answered', []))
        existing_answered.update(answered_indices)
        progress[file_key]['answered'] = sorted(list(existing_answered))
        progress[file_key]['total_questions'] = len(original_questions)
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def reset_progress(self, file_key):
        """Reset progress for a specific file"""
        progress = self.load_progress()
        if file_key in progress:
            del progress[file_key]
            try:
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, indent=2)
            except:
                pass
    
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
        randomized = []
        for question in questions:
            q_copy = question.copy()
            q_copy['choices'] = question['choices'].copy()
            correct_answer = q_copy["choices"][q_copy["correct"]]
            random.shuffle(q_copy["choices"])
            q_copy["correct"] = q_copy["choices"].index(correct_answer)
            randomized.append(q_copy)
        return randomized
    
    def create_quiz_screen(self):
        """Create the quiz interface with 10 questions"""
        self.clear_window()
        
        start_idx = self.current_batch_idx * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.questions))
        current_batch = self.questions[start_idx:end_idx]
        
        # Mark these questions as seen
        for i in range(start_idx, end_idx):
            self.seen_questions.add(i)
        
        # Header frame
        header_frame = tk.Frame(self.root, bg="#2196F3", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        progress_label = tk.Label(header_frame, 
                                 text=f"Questions {start_idx + 1}-{end_idx} of {len(self.questions)}", 
                                 font=("Arial", 16, "bold"), bg="#2196F3", fg="white")
        progress_label.pack(pady=20)
        
        # Create scrollable frame
        canvas_frame = tk.Frame(self.root, bg="#f0f0f0")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create questions
        self.answer_vars = []
        for i, question in enumerate(current_batch):
            question_idx = start_idx + i
            
            # Question frame
            q_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", borderwidth=1)
            q_frame.pack(fill="x", pady=10, padx=10)
            
            # Question number and text
            q_label = tk.Label(q_frame, 
                              text=f"Question {question_idx + 1}: {question['question']}", 
                              font=("Arial", 13, "bold"), 
                              bg="white", 
                              wraplength=700,
                              justify="left",
                              anchor="w")
            q_label.pack(fill="x", padx=15, pady=(15, 10))
            
            # Radio buttons for choices
            answer_var = tk.IntVar(value=-1)
            self.answer_vars.append(answer_var)
            
            for j, choice in enumerate(question["choices"]):
                rb = tk.Radiobutton(q_frame, 
                                   text=choice, 
                                   variable=answer_var, 
                                   value=j,
                                   font=("Arial", 12),
                                   bg="white",
                                   activebackground="white",
                                   padx=30,
                                   pady=5,
                                   wraplength=650,
                                   justify="left")
                rb.pack(anchor="w", padx=15)
            
            # Add some space at the bottom
            tk.Frame(q_frame, bg="white", height=10).pack()
        
        # Submit button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0", height=70)
        button_frame.pack(fill="x")
        button_frame.pack_propagate(False)
        
        submit_btn = tk.Button(button_frame, 
                              text="Submit Answers", 
                              command=lambda: self.show_answers(start_idx, end_idx),
                              font=("Arial", 14, "bold"),
                              bg="#4CAF50",
                              fg="white",
                              padx=40,
                              pady=10,
                              cursor="hand2")
        submit_btn.pack(pady=15)
        
        # Store canvas reference for cleanup
        self.canvas = canvas
    
    def show_answers(self, start_idx, end_idx):
        """Show all answers and explanations for the current batch"""
        # Check if all questions are answered
        unanswered = []
        for i, var in enumerate(self.answer_vars):
            if var.get() == -1:
                unanswered.append(i + 1)
        
        if unanswered:
            messagebox.showwarning("Incomplete", 
                                  f"Please answer all questions!\nUnanswered: {', '.join(map(str, unanswered))}")
            return
        
        # Calculate score for this batch
        batch_score = 0
        for i, var in enumerate(self.answer_vars):
            question_idx = start_idx + i
            if var.get() == self.questions[question_idx]["correct"]:
                batch_score += 1
            self.user_answers[question_idx] = var.get()
        
        self.total_score += batch_score
        
        # Save progress after each batch
        self.save_progress()
        
        # Unbind mousewheel from old canvas
        if hasattr(self, 'canvas'):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Show results screen
        self.show_results_screen(start_idx, end_idx, batch_score)
    
    def show_results_screen(self, start_idx, end_idx, batch_score):
        """Display results with answers and explanations"""
        self.clear_window()
        
        current_batch = self.questions[start_idx:end_idx]
        
        # Header frame
        header_frame = tk.Frame(self.root, bg="#2196F3", height=90)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text=f"Results: Questions {start_idx + 1}-{end_idx}", 
                              font=("Arial", 16, "bold"), bg="#2196F3", fg="white")
        title_label.pack(pady=10)
        
        score_label = tk.Label(header_frame, 
                              text=f"Score: {batch_score}/{len(current_batch)} ({batch_score/len(current_batch)*100:.1f}%)", 
                              font=("Arial", 14), bg="#2196F3", fg="white")
        score_label.pack()
        
        # Create scrollable frame
        canvas_frame = tk.Frame(self.root, bg="#f0f0f0")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Display each question with answer
        for i, question in enumerate(current_batch):
            question_idx = start_idx + i
            user_answer = self.user_answers[question_idx]
            correct_answer = question["correct"]
            is_correct = user_answer == correct_answer
            
            # Question frame
            q_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", borderwidth=2,
                             highlightbackground="#4CAF50" if is_correct else "#f44336",
                             highlightthickness=3)
            q_frame.pack(fill="x", pady=10, padx=10)
            
            # Status banner
            status_frame = tk.Frame(q_frame, bg="#4CAF50" if is_correct else "#f44336", height=30)
            status_frame.pack(fill="x")
            status_label = tk.Label(status_frame, 
                                   text="✓ CORRECT" if is_correct else "✗ INCORRECT",
                                   font=("Arial", 11, "bold"),
                                   bg="#4CAF50" if is_correct else "#f44336",
                                   fg="white")
            status_label.pack(pady=5)
            
            # Question text
            q_label = tk.Label(q_frame, 
                              text=f"Question {question_idx + 1}: {question['question']}", 
                              font=("Arial", 13, "bold"), 
                              bg="white", 
                              wraplength=700,
                              justify="left",
                              anchor="w")
            q_label.pack(fill="x", padx=15, pady=(10, 5))
            
            # Show all choices with indicators
            for j, choice in enumerate(question["choices"]):
                choice_frame = tk.Frame(q_frame, bg="white")
                choice_frame.pack(fill="x", padx=15, pady=2)
                
                if j == correct_answer:
                    indicator = "✓"
                    color = "#4CAF50"
                    weight = "bold"
                elif j == user_answer and not is_correct:
                    indicator = "✗"
                    color = "#f44336"
                    weight = "bold"
                else:
                    indicator = "○"
                    color = "#666"
                    weight = "normal"
                
                choice_label = tk.Label(choice_frame, 
                                       text=f"{indicator} {choice}",
                                       font=("Arial", 11, weight),
                                       bg="white",
                                       fg=color,
                                       wraplength=680,
                                       justify="left",
                                       anchor="w")
                choice_label.pack(anchor="w", padx=20)
            
            # Explanation
            exp_frame = tk.Frame(q_frame, bg="#e3f2fd")
            exp_frame.pack(fill="x", padx=15, pady=10)
            
            exp_title = tk.Label(exp_frame, text="Explanation:", 
                                font=("Arial", 11, "bold"), 
                                bg="#e3f2fd", fg="#1976D2")
            exp_title.pack(anchor="w", padx=10, pady=(5, 0))
            
            exp_label = tk.Label(exp_frame, 
                                text=question["explanation"],
                                font=("Arial", 11),
                                bg="#e3f2fd",
                                fg="#333",
                                wraplength=680,
                                justify="left",
                                anchor="w")
            exp_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Navigation buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0", height=70)
        button_frame.pack(fill="x")
        button_frame.pack_propagate(False)
        
        btn_container = tk.Frame(button_frame, bg="#f0f0f0")
        btn_container.pack(expand=True)
        
        if end_idx < len(self.questions):
            next_btn = tk.Button(btn_container, 
                                text="Next 10 Questions →", 
                                command=self.next_batch,
                                font=("Arial", 14, "bold"),
                                bg="#2196F3",
                                fg="white",
                                padx=30,
                                pady=10,
                                cursor="hand2")
            next_btn.pack(side="left", padx=10)
        else:
            finish_btn = tk.Button(btn_container, 
                                  text="Finish Quiz", 
                                  command=self.show_final_results,
                                  font=("Arial", 14, "bold"),
                                  bg="#4CAF50",
                                  fg="white",
                                  padx=30,
                                  pady=10,
                                  cursor="hand2")
            finish_btn.pack(side="left", padx=10)
        
        restart_btn = tk.Button(btn_container, 
                               text="New Quiz", 
                               command=self.create_start_screen,
                               font=("Arial", 14),
                               bg="#f44336",
                               fg="white",
                               padx=30,
                               pady=10,
                               cursor="hand2")
        restart_btn.pack(side="left", padx=10)
        
        # Store canvas reference for cleanup
        self.canvas = canvas
    
    def next_batch(self):
        """Move to next batch of questions"""
        # Unbind mousewheel from old canvas
        if hasattr(self, 'canvas'):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.current_batch_idx += 1
        self.create_quiz_screen()
    
    def show_final_results(self):
        """Display final quiz results"""
        # Unbind mousewheel from old canvas
        if hasattr(self, 'canvas'):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.clear_window()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = tk.Label(frame, text="Quiz Complete!", 
                              font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#4CAF50")
        title_label.pack(pady=20)
        
        percentage = (self.total_score / len(self.questions)) * 100
        score_label = tk.Label(frame, 
                              text=f"Final Score: {self.total_score}/{len(self.questions)}", 
                              font=("Arial", 20), bg="#f0f0f0", fg="#333")
        score_label.pack(pady=10)
        
        percentage_label = tk.Label(frame, 
                                   text=f"({percentage:.1f}%)", 
                                   font=("Arial", 16), bg="#f0f0f0", fg="#666")
        percentage_label.pack(pady=5)
        
        # Feedback
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
        
        # Show progress info
        if self.current_file_path:
            progress = self.load_progress()
            file_key = self.get_file_key(self.current_file_path)
            if file_key in progress:
                total = progress[file_key].get('total_questions', 0)
                answered = len(progress[file_key].get('answered', []))
                progress_label = tk.Label(frame, 
                                        text=f"Total Progress: {answered}/{total} questions attempted", 
                                        font=("Arial", 11), bg="#f0f0f0", fg="#666")
                progress_label.pack(pady=5)
        
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
        # Unbind mousewheel before clearing
        if hasattr(self, 'canvas'):
            try:
                self.canvas.unbind_all("<MouseWheel>")
            except:
                pass
        
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()