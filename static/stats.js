function toggleBooks(moodId) {
    const list = document.getElementById("books-" + moodId);
    list.classList.toggle("expanded");
  }
  
  const moodBackgrounds = moodLabels.map(mood => moodColorMap[mood] || '#ccc');
  
  new Chart(document.getElementById('moodChart'), {
    type: 'pie',
    data: {
      labels: moodLabels,
      datasets: [{
        data: moodValues,
        backgroundColor: moodBackgrounds
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.parsed}`;
            }
          }
        }
      }
    }
  });
  
  const ratingColors = ratingMoods.map(mood => moodColorMap[mood] || '#ccc');
  
  new Chart(document.getElementById('ratingByMoodChart'), {
    type: 'bar',
    data: {
      labels: ratingMoods,
      datasets: [{
        label: 'Avg Rating',
        data: ratingValues,
        backgroundColor: ratingColors
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 5
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.parsed}`;
            }
          }
        }
      }
    }
  });
  
  new Chart(document.getElementById('booksPerRatingChart'), {
    type: 'bar',
    data: {
      labels: booksPerRatingLabels,
      datasets: [{
        label: 'Books',
        data: booksPerRatingValues,
        backgroundColor: '#ffc6ff'
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.parsed}`;
            }
          }
        }
      }
    }
  });
  