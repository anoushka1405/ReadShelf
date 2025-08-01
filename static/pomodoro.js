document.addEventListener("DOMContentLoaded", () => {
  // Pomodoro Timer Setup
  let isRunning = false;
  let isWorkSession = true;
  let timer;
  let timeLeft = 25 * 60;

  let sessionsCompleted = 0;
  let totalReadMinutes = 0;

  const workDuration = 25 * 60;
  const breakDuration = 5 * 60;

  const timeDisplay = document.getElementById("time");
  const startBtn = document.getElementById("start-btn");
  const pauseBtn = document.getElementById("pause-btn");
  const resetBtn = document.getElementById("reset-btn");
  const sessionCount = document.getElementById("session-count");
  const totalTime = document.getElementById("total-time");
  const sessionLabel = document.querySelector("h2");

  const wordForm = document.getElementById("word-form");
  const wordList = document.getElementById("word-list");
  const wordInput = document.getElementById("word-input");

  function updateDisplay() {
    const minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
    const seconds = (timeLeft % 60).toString().padStart(2, '0');
    timeDisplay.textContent = `${minutes}:${seconds}`;
    sessionLabel.textContent = isWorkSession ? "Focus Time 🧠" : "Break Time ☕";
  }

  function tick() {
    if (timeLeft > 0) {
      timeLeft--;
      updateDisplay();
    } else {
      clearInterval(timer);
      isRunning = false;

      if (isWorkSession) {
        sessionsCompleted++;
        totalReadMinutes += 25;
        sessionCount.textContent = `Sessions completed: ${sessionsCompleted}`;
        totalTime.textContent = `Total read time: ${totalReadMinutes} mins`;
        confetti(); // 🎉
        alert("Break time! Click Start when you're ready to relax ☕");
      } else {
        alert("Back to reading! Click Start for your next Pomodoro 📚");
      }

      isWorkSession = !isWorkSession;
      timeLeft = isWorkSession ? workDuration : breakDuration;
      updateDisplay();

      startBtn.disabled = false;
      pauseBtn.disabled = true;
    }
  }

  startBtn.addEventListener("click", () => {
    if (!isRunning) {
      timer = setInterval(tick, 1000);
      isRunning = true;
      startBtn.disabled = true;
      pauseBtn.disabled = false;
    }
  });

  pauseBtn.addEventListener("click", () => {
    clearInterval(timer);
    isRunning = false;
    startBtn.disabled = false;
    pauseBtn.disabled = true;
  });

  resetBtn.addEventListener("click", () => {
    clearInterval(timer);
    isRunning = false;
    timeLeft = isWorkSession ? workDuration : breakDuration;
    updateDisplay();
    startBtn.disabled = false;
    pauseBtn.disabled = true;
  });

  updateDisplay();

  // Word Vault Logic (no book-wise storage)
  if (wordForm) {
    wordForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const word = wordInput.value.trim();
      if (!word) {
        alert("Please enter a word.");
        return;
      }

      try {
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`);
        const data = await response.json();

        if (data.title === "No Definitions Found") {
          alert(`No definition found for "${word}".`);
          return;
        }

        const meaning = data[0].meanings[0].definitions[0].definition;

        const li = document.createElement("li");
        li.innerHTML = `<strong>${word}</strong> — ${meaning}`;
        wordList.appendChild(li);

        wordInput.value = "";
      } catch (error) {
        console.error("Error fetching definition:", error);
        alert("Something went wrong. Please try again.");
      }
    });
  }
});
