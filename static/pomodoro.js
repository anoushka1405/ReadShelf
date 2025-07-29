let isRunning = false;
let isWorkSession = true;
let timer;
let timeLeft = 25 * 60;

let sessionsCompleted = 0;
let totalReadMinutes = 0;

const workDuration = 25 * 60;
const breakDuration = 5 * 60;

// DOM Elements
const timeDisplay = document.getElementById("time");
const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const resetBtn = document.getElementById("reset-btn");
const sessionCount = document.getElementById("session-count");
const totalTime = document.getElementById("total-time");
const sessionLabel = document.querySelector("h2");

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

    // Re-enable Start, disable Pause
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

// Initial display
updateDisplay();
