import { Platform } from 'quasar';
import { Share } from '@capacitor/share';

export const shareContent = async (title, url, text) => {
  try {
    if (Platform.is.capacitor) {
      // Usar Capacitor Share para dispositivos móviles
      await Share.share({
        title: title,
        text: text,
        url: url,
        dialogTitle: 'Compartir', // Solo para Android
      });
      console.log('Contenido compartido exitosamente (Capacitor)');
    } else if (navigator.share) {
      // Usar Web Share API para navegadores compatibles
      await navigator.share({
        title: title,
        url: url,
        text: text,
      });
      console.log('Contenido compartido exitosamente (Web Share API)');
    } else {
      // Opción de respaldo para navegadores no compatibles
      const shareUrl = encodeURIComponent(url);
      window.open(`mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(text + '\n\n' + url)}`);
      console.log('Abrir cliente de correo para compartir');
    }
  } catch (error) {
    console.error('Error al compartir:', error.message);
  }
};