const questionInput = document.getElementById("question-input");
const answerOutput = document.getElementById("answer-output");
const askButton = document.getElementById("ask-button");

const showAnswer = (text, isError = false) => {
  answerOutput.textContent = text;
  answerOutput.classList.toggle("loading", false);
  answerOutput.style.color = isError ? "#f87171" : "var(--text)";
};

const setLoading = () => {
  answerOutput.textContent = "Waiting for the agent...";
  answerOutput.classList.add("loading");
  answerOutput.style.color = "var(--muted)";
};

const askAgent = async () => {
  const question = questionInput.value.trim();
  if (!question) {
    showAnswer("Please type a question before asking.", true);
    return;
  }

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
      const errorData = await response.json();
      throw new Error(errorData.detail || "Agent request failed.");
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
