// src/helpers/loadingUtils.js
import { Notify } from 'quasar';

/**
 * Ejecuta una tarea asíncrona mostrando el indicador global QLoading
 * durante una duración mínima especificada.
 *
 * @async
 * @param {object} $q - La instancia del objeto $q de Quasar (obtenida con useQuasar()).
 * @param {Function} task - La función asíncrona que realiza el trabajo (ej. llamada API). Debe retornar los datos o lanzar un error.
 * @param {number} [minDuration=500] - Tiempo mínimo en milisegundos para mostrar el indicador de carga. Default: 500ms.
 * @param {object} [loadingOptions={}] - Opciones adicionales para pasar a $q.loading.show() y sobrescribir los defaults.
 * @returns {Promise<any>} Una promesa que resuelve con el resultado de la tarea 'task', o rechaza si 'task' lanza un error.
 * @throws {Error} Lanza el error original si la 'task' falla.
 */
export async function runTaskWithMinLoading(
  $q,
  task,
  minDuration = 500, // Un default razonable, ajústalo si prefieres
  loadingOptions = {}
) {
  // Validación básica de entradas
  if (!$q || typeof $q.loading?.show !== 'function') {
    console.error('runTaskWithMinLoading: Se requiere el objeto $q con el plugin Loading.');
    // Intenta ejecutar la tarea sin loading como fallback
    try {
       return await task();
    } catch(err) {
       // Notifica el error incluso en el fallback
       Notify.create({ type: 'negative', message: 'Ocurrió un error inesperado.', caption: err.message });
       throw err;
    }
  }
  if (typeof task !== 'function') {
    const error = new Error('runTaskWithMinLoading: el parámetro "task" debe ser una función asíncrona.');
    console.error(error);
    return Promise.reject(error);
  }

  // Mostrar el loading (usará defaults + las loadingOptions que pases)
  $q.loading.show(loadingOptions);

  const timerPromise = new Promise(resolve => setTimeout(resolve, minDuration));
  let taskResult;
  let taskError;

  // Ejecutar la tarea real y capturar su resultado o error
  const taskPromise = task().then(result => {
    taskResult = result;
  }).catch(err => {
    taskError = err; // Capturar el error para manejarlo después
    console.error('Error durante la ejecución de la tarea en runTaskWithMinLoading:', err);
     // Opcional: Notificación genérica de error desde el util
     Notify.create({
       type: 'negative',
       message: 'Falló la operación.',
       caption: err?.message || 'Error desconocido'
     });
  });


  try {
    // Esperar a que tanto la tarea (o su intento) como el temporizador terminen
    await Promise.all([taskPromise, timerPromise]);
  } finally {
    // Siempre ocultar el loading al finalizar
    $q.loading.hide();
  }

  // Después de ocultar, si hubo un error en la tarea, lanzarlo de nuevo
  if (taskError) {
    throw taskError; // Permite que el componente que llama pueda hacer try/catch
  }

  // Si todo fue bien, devolver el resultado de la tarea
  return taskResult;
}