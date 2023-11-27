document.addEventListener('DOMContentLoaded', function () {
  const clickButton = document.getElementById('click-me');
  const clickCountDisplay = document.getElementById('click-count');
  
  clickButton.addEventListener('click', function () {
    fetch('/toggle_count', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // No need to send data, as the server tracks the toggle state
    })
    .then(response => response.json())
    .then(data => {
      clickCountDisplay.textContent = data.click_count;
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  });
});

