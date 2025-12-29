const buttons = document.querySelectorAll(".rps-btn");
const resultEl = document.getElementById("result");
const scoreEl = document.getElementById("score");

let playerScore = 0;
let computerScore = 0;

buttons.forEach(btn => {
    btn.addEventListener("click", () => {
        const playerChoice = btn.dataset.choice;
        const choices = ["rock", "paper", "scissors"];
        const computerChoice = choices[Math.floor(Math.random() * 3)];

        let outcome = "";

        if (playerChoice === computerChoice) outcome = "It's a tie!";
        else if (
            (playerChoice === "rock" && computerChoice === "scissors") ||
            (playerChoice === "paper" && computerChoice === "rock") ||
            (playerChoice === "scissors" && computerChoice === "paper")
        ) {
            outcome = "You win!";
            playerScore++;
        } else {
            outcome = "You lose!";
            computerScore++;
        }

        resultEl.textContent = `You: ${playerChoice} | Computer: ${computerChoice} → ${outcome}`;
        scoreEl.textContent = `Score → You: ${playerScore} | Computer: ${computerScore}`;
    });
});
