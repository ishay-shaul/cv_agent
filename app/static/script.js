const questionInput = document.getElementById("question-input");
const answerPanel = document.getElementById("answer-panel");
const answerOutput = document.getElementById("answer-output");
const askButton = document.getElementById("ask-button");
const questionHint = document.getElementById("question-hint");

const resetButton = () => {
  askButton.disabled = false;
};

const showAnswer = (text, isError = false) => {
  answerPanel.hidden = false;
  answerOutput.textContent = text;
  answerOutput.classList.remove("loading");
  answerOutput.classList.toggle("error", isError);
  resetButton();
};

const setLoading = () => {
  answerPanel.hidden = false;
  answerOutput.textContent = "Waiting for the answer...";
  answerOutput.classList.add("loading");
  answerOutput.classList.remove("error");
  askButton.disabled = true;
  answerPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
};

const showHint = (text) => {
  questionHint.hidden = false;
  questionHint.textContent = text;
};

const clearHint = () => {
  questionHint.hidden = true;
  questionHint.textContent = "";
};

const askAgent = async () => {
  const question = questionInput.value.trim();
  if (!question) {
    showHint("Type a question in the box above, then click Ask.");
    questionInput.focus();
    return;
  }

  clearHint();
  setLoading();

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      let detail = "The agent could not answer that question.";
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          detail = errorData.detail;
        }
      } catch (_parseError) {
        // Keep the fallback message when the server does not return JSON.
      }
      throw new Error(detail);
    }

    const result = await response.json();
    showAnswer(result.answer || "No answer returned.");
  } catch (error) {
    showAnswer(error.message || "Unable to reach the agent.", true);
  }
};

askButton.addEventListener("click", askAgent);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    askAgent();
  }
});
questionInput.addEventListener("input", () => {
  if (questionInput.value.trim()) {
    clearHint();
  }
});
