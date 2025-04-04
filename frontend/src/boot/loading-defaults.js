// src/boot/loading-defaults.js
import { boot } from 'quasar/wrappers';
// ¡Aquí sí puedes importar tu componente sin problemas!
import PadelPlayLogoSpinner from 'src/components/PadelPlayLogoSpinner.vue';

export default boot(({ app }) => {
  // Accedemos al objeto $q disponible globalmente en la app Vue
  const $q = app.config.globalProperties.$q;

  // Establecemos los valores por defecto para el plugin QLoading
  $q.loading.setDefaults({
    spinner: PadelPlayLogoSpinner, // ¡Usamos el componente importado!
    backgroundColor: 'black',
    message: '',
    messageColor: 'white',

    // Aquí también puedes añadir otras configuraciones por defecto
    // que antes tenías en quasar.config.js, si quieres:
    // spinnerColor: 'primary',
    // message: 'Cargando...',
    // backgroundColor: 'rgba(0, 0, 0, 0.7)',
  });
});