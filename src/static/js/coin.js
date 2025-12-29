const coin = document.getElementById('coin');
const result = document.getElementById('result');

coin.style.transform = "rotateY(0deg)"; // start at Heads

coin.addEventListener('click', () => {
    const toss = Math.random() < 0.5 ? 'Heads' : 'Tails';
    const flips = 6; // full rotations for effect

    // Reset rotation instantly to 0° (Heads)
    coin.style.transition = "none";
    coin.style.transform = "rotateY(0deg)";
    void coin.offsetWidth; // force reflow

    // Animate flip to desired result
    const finalRotation = flips * 360 + (toss === 'Tails' ? 180 : 0);
    coin.style.transition = "transform 1s ease-in-out";
    coin.style.transform = `rotateY(${finalRotation}deg)`;

    // Update result after animation
    setTimeout(() => {
        result.textContent = toss;
    }, 1000);
});
