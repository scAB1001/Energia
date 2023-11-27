// Source: https://github.com/CodeSteppe/card-swiper

// DOM
const swiper = document.querySelector('#swiper');
const like = document.querySelector('#like');
const dislike = document.querySelector('#dislike');

// Variables
let cardCount = 0;

// Functions
function appendNewCard(carData) {
  const card = new Card({
    carID: carData.carID,
    imageUrl: carData.imageUrl,
    carName: carData.carName,
    details: carData.details,
    
    onDismiss: appendNewCard,
    onLike: () => {
      console.log(`${carData.carName} liked`); // CONFIRMATION
      like.style.animationPlayState = 'running';
      like.classList.toggle('trigger');
    },
    onDislike: () => {
      console.log(`${carData.carName} disliked`); // CONFIRMATION
      dislike.style.animationPlayState = 'running';
      dislike.classList.toggle('trigger');
    }

  });
  /* ERROR: Like/dislike don't get animated
   * When console.log is in the onLike: scope, it does not get caught ever.
   * This suggests the dismiss, onLike/Dislike are never caught
  */ 
  cardCount++;
  console.log(`card${cardCount} added`);  
  swiper.append(card.element);

  const cards = swiper.querySelectorAll('.card:not(.dismissing)');
  cards.forEach((card, index) => {
    card.style.setProperty('--i', index);
  });
}

// Load the initial cards
cars.forEach((carData) => {
  appendNewCard(carData);
});