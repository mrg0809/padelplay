export function shareProfile() {
    if (navigator.share) {
      navigator
        .share({
          title: "Mi Perfil de Padel",
          text: "Mira mi perfil en la app de PadelPlay!",
          url: window.location.href,
        })
        .catch(console.error);
    } else {
      alert("Tu navegador no soporta compartir enlaces.");
    }
  }
  