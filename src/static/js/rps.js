document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".rps-btn");
    const resultEl = document.getElementById("result");
    const scoreEl = document.getElementById("score");
    const balanceEl = document.getElementById("balance");
    const multiplierSlider = document.getElementById("multiplier");
    const multiplierText = document.getElementById("multiplier-text");
    const formScore = document.getElementById("form-score");
    const saveForm = document.getElementById("save-form");
    const balanceToSend = document.getElementById("balance-to-send");
    const endBtn = document.getElementById("end-session");

    let score = 0;
    let balance = parseFloat(balanceEl.textContent.replace("Balance: $", ""));
    let multiplier = parseInt(multiplierSlider.value);

    multiplierSlider.oninput = () => {
        multiplier = parseInt(multiplierSlider.value);
        multiplierText.textContent = multiplier;
    };

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const playerChoice = btn.dataset.choice;
            const choices = ["rock", "paper", "scissors"];
            const computerChoice = choices[Math.floor(Math.random() * 3)];

            let change = 0;
            let outcome = "";

            if (playerChoice === computerChoice) {
                outcome = "It's a tie!";
            } else if (
                (playerChoice === "rock" && computerChoice === "scissors") ||
                (playerChoice === "paper" && computerChoice === "rock") ||
                (playerChoice === "scissors" && computerChoice === "paper")
            ) {
                outcome = "You win!";
                change = multiplier;
            } else {
                outcome = "You lose!";
                change = -multiplier;
            }

            balance += change;
            score += change;

            resultEl.textContent = `You: ${playerChoice} | Computer: ${computerChoice} → ${outcome}`;
            scoreEl.textContent = `Score: ${score}`;
            balanceEl.textContent = `Balance: $${balance}`;

            formScore.value = score;
            balanceToSend.value = balance;

            if (balance <= 0) {
                saveForm.submit();
            }
        });
    });

    endBtn.addEventListener("click", () => {
        formScore.value = score;
        balanceToSend.value = balance;
        saveForm.submit();
    });
});
