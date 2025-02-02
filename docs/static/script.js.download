// static/js/script.js

document.addEventListener("DOMContentLoaded", function() {
    // Dynamic greeting message
    const dynamicContent = document.getElementById('dynamic-content');
    if (dynamicContent) {
      const tips = [
        "Tip of the Day: Stay organized by keeping your notes sorted!",
        "Did you know? Regular breaks can boost your study efficiency!",
        "Fun Fact: Revising with flashcards is a proven memory booster.",
        "Remember: Practice makes perfect. Keep working hard!"
      ];
      // Pick a random tip to display.
      const randomTip = tips[Math.floor(Math.random() * tips.length)];
      
      // Create a new element and add a fade-in effect using CSS class (defined in your CSS file)
      const tipElement = document.createElement('p');
      tipElement.classList.add('fade-in-tip');
      tipElement.textContent = randomTip;
      
      dynamicContent.appendChild(tipElement);
    }
  
    // Example: A simple animation function for an interactive welcome message
    const homeContainer = document.querySelector('.home-container');
    if (homeContainer) {
      homeContainer.style.opacity = 0;
      let opacity = 0;
      const fadeIn = setInterval(() => {
        opacity += 0.02;
        homeContainer.style.opacity = opacity;
        if (opacity >= 1) clearInterval(fadeIn);
      }, 30);
    }
  });
  