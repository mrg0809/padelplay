<template>
      <div class="promo-bar">
        <div class="promo-text">
          🚀 ¡Promoción especial! 20% de descuento en reservas antes del viernes. 🎉
        </div>
    </div>
  </template>
  
  <style scoped>
  /* Contenedor de la barra promocional */
  .promo-bar {
    background-color: #ffffff; /* Fondo blanco */
    color: #333333; /* Texto oscuro */
    width: 100%;
    overflow: hidden; /* Oculta contenido fuera del área visible */
    height: 30px; /* Altura de la barra */
    border-bottom: 1px solid #e0e0e0; /* Línea sutil para separar */
    display: flex;
    align-items: center;
  }
  
  /* Texto de la promoción con animación */
  .promo-text {
    white-space: nowrap; /* Evita que el texto se divida en líneas */
    display: inline-block;
    animation: scroll-text 10s linear infinite; /* Animación continua */
  }
  
  /* Animación de desplazamiento */
  @keyframes scroll-text {
    0% {
      transform: translateX(100%); /* Empieza fuera del área visible */
    }
    100% {
      transform: translateX(-100%); /* Termina fuera del área visible por la izquierda */
    }
  }
  </style>
  