<template>
      <div class="promo-bar">
        <div class="promo-text">
          🚀 ¡Promoción especial! 20% de descuento en reservas antes del viernes. 🎉
        </div>
    </div>
  </template>
  
  <style scoped>
  .promo-bar {
    background-color: #ffffff; 
    color: #333333; /* Texto oscuro */
    width: 100%;
    overflow: hidden; /* Oculta contenido fuera del área visible */
    height: 30px; 
    border-bottom: 1px solid #e0e0e0; 
    display: flex;
    align-items: center;
  }
  
  /* Texto de la promoción con animación */
  .promo-text {
    white-space: nowrap; /* Evita que el texto se divida en líneas */
    display: inline-block;
    animation: scroll-text 10s linear infinite; 
  }
  
  /* Animación de desplazamiento */
  @keyframes scroll-text {
    0% {
      transform: translateX(100%); 
    }
    100% {
      transform: translateX(-100%); 
    }
  }
  </style>
  