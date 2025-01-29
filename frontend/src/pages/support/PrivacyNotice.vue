<template>
    <q-layout view="hHh lpR fFf">
        <q-header elevated class="bg-primary text-white">
            <div class="header-content">
                <div class="greeting">
                <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
                </div>
                <div class="header-icons">
                <q-btn flat round icon="close" @click="goBack" />
                </div>
            </div>
        </q-header>
        <q-page-container>
    <q-page class="q-pa-md">
  
      <div class="text-black text-h4 q-mb-md">Aviso de Privacidad</div>
  
      <q-tabs v-model="activeTab" class="text-primary">
        <q-tab name="responsible" label="Responsable" />
        <q-tab name="processing" label="Tratamiento de Datos" />
        <q-tab name="retention" label="Conservación de Datos" />
        <q-tab name="origin" label="Origen de los Datos" />
        <q-tab name="sharing" label="Cesiones de Datos" />
        <q-tab name="protection" label="Protección de Datos" />
        <q-tab name="rights" label="Derechos del Usuario" />
      </q-tabs>
  
      <q-separator />
  
      <q-tab-panels v-model="activeTab" class="tabs" animated>
  
        <q-tab-panel name="responsible">
          <div class="text-h5 q-mb-md">1. ¿QUIÉN ES EL RESPONSABLE DEL TRATAMIENTO?</div>
          <p>
            Sus datos personales serán tratados por Grupo Empresarial Play SA de CV. (en adelante, también "PADELPLAY"), con domicilio social en Calle Agustin de la Rosa 757, Colonia Ladrón de Guevara CP 44600, Guadalajara Jalisco que actuará en calidad de "Responsable del tratamiento de los datos".
          </p>
          <p>
            Podrá contactar con el responsable del tratamiento de los datos en la siguiente dirección de correo electrónico: <a href="mailto:contacto@padelplay.mx">contacto@padelplay.mx</a>.
          </p>
          <p>
            Para garantizar la adecuada gestión en el tratamiento de sus datos, PADELPLAY tiene designado un Delegado de Protección de Datos (en adelante, DPO), a quien podrá dirigirse para cualquier cuestión que precise y con quien puede contactar en la dirección electrónica <a href="mailto:jesus.gutierrez@padelplay.mx">jesus.gutierrez@padelplay.mx</a>.
          </p>
        </q-tab-panel>
  
        <q-tab-panel name="processing">
          <div class="text-h5 q-mb-md">2. ¿CÓMO Y POR QUÉ TRATAREMOS SUS DATOS PERSONALES?</div>
          <p>Los datos personales tratados a través de la presente página web pueden ser tratados por PADEL PLAY para las siguientes finalidades:</p>
  
          <q-list bordered separator>
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 1. Gestión de la cuenta de usuario</q-item-label>
                <q-item-label caption>
                  Creación de una cuenta y gestión de su perfil (reservas en clubes deportivos y compras a través de la App).
                  Datos tratados: Datos identificativos, características personales y datos financieros.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 2. Atención al cliente</q-item-label>
                <q-item-label caption>
                  Prestar los servicios y la información solicitada, tanto por vía chatbot, como por vías convencionales.
                  Datos tratados: Datos identificativos.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 3. Envío de comunicaciones comerciales propias</q-item-label>
                <q-item-label caption>
                  Envío de comunicaciones comerciales sobre productos, servicios y actividades ofertadas por PADELPLAY que pudiera resultar de interés a los usuarios a través de medios convencionales y electrónicos (correo electrónico, SMS y medios análogos).
                  Datos tratados: Datos identificativos y número de teléfono.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 4. Análisis del comportamiento de los usuarios con fuentes internas</q-item-label>
                <q-item-label caption>
                  Análisis de la navegación en la App para optimizar y mejorar la experiencia del Usuario.
                  Datos tratados: Datos identificativos, características personales y sociales (en su caso).
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 5. Envío de encuestas de satisfacción</q-item-label>
                <q-item-label caption>
                  Envío a los usuarios de cuestionarios y encuestas con el fin de recabar información sobre los servicios ofrecidos.
                  Datos tratados: Datos identificativos.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 6. Comunicaciones transaccionales desarrolladas en el marco del Servicio</q-item-label>
                <q-item-label caption>
                  Comunicaciones realizadas por medios convencionales y/o electrónicos al medio de contacto facilitado por el Usuario para el desarrollo, control, mantenimiento y ejecución del Servicio.
                  Datos tratados: Datos identificativos y de contacto.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 7. Cumplimiento de la normativa aplicable</q-item-label>
                <q-item-label caption>
                  Cumplimiento con aquellas obligaciones legales impuestas a PADELPLAY en cualquier orden.
                  Datos tratados: Datos identificativos y de contacto; Datos derivados del uso del servicio.
                </q-item-label>
              </q-item-section>
            </q-item>
  
            <q-item clickable v-ripple>
              <q-item-section>
                <q-item-label>Finalidad 8. Geolocalización del Usuario</q-item-label>
                <q-item-label caption>
                  Obtención de datos de geolocalización a través del dispositivo o terminal digital personal del Usuario para permitir una mejor prestación de los servicios puestos a disposición a través de la App.
                  Datos tratados: Datos identificativos de geolocalización.
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-tab-panel>
  
        <q-tab-panel name="retention">
          <div class="text-h5 q-mb-md">3. PLAZOS DE CONSERVACIÓN DE LOS DATOS PERSONALES.</div>
          <p>
            Los datos personales proporcionados por el Usuario se conservarán mientras permanezca de alta en la App, sin perjuicio de los derechos que se regulan en esta Condición y en la condición 7. Asimismo, podrán conservarse cuando sean necesarios para el cumplimiento de una obligación legal o para la formulación, el ejercicio y la defensa de reclamaciones.
          </p>
          <p>
            Si el Usuario revoca su consentimiento o ejercita los derechos de cancelación o supresión, sus datos se conservarán bloqueados a disposición de la autoridades gubernamentales durante los plazos establecidos legalmente para atender a las posibles responsabilidades originadas  del tratamiento de los datos personales.
          </p>
          <p>
            En cualquier caso, el Usuario puede solicitar información detallada sobre los plazos de conservación de datos aplicados poniéndose en contacto a través de jesus.gutierrez@padelplay.com.
          </p>
        </q-tab-panel>
  
        <q-tab-panel name="origin">
          <div class="text-h5 q-mb-md">4. ORIGEN DE LOS DATOS PERSONALES.</div>
          <p>
            Los datos personales que tratará PADELPLAY han sido facilitados en su gran mayoría de manera directa por el propio Usuario, tales como el nombre, los apellidos, dirección, datos de contacto. El Usuario se responsabiliza de su veracidad y actualización.
          </p>
          <p>
            PADELPLAY podrá obtener información recogida a través de la App, así como de intereses y consumo a través de su participación como Usuario, tales como datos estadísticos o de navegación.
          </p>
          <p>
            Asimismo, si el Usuario ha accedido a la web de PADELPLAY a través de un "login" de redes sociales, PADELPLAY podrá obtener la información pública disponible por Internet como su identificador de usuario, nombre, sexo, fecha de nacimiento e información del perfil como su biografía y la información de ubicación (si fue declarada por el usuario). En el caso de Facebook, el Participante podrá seleccionar entre los permisos que le son solicitados, aquellos que no desee proporcionar.
          </p>
          <p>
            Se informa al Usuario de la posibilidad de editar la información que quiere compartir con PADELPLAY, pudiendo permitir un acceso más amplio o restringido a su información según desee, así como la posibilidad de que dispone de revocar en cualquier momento el consentimiento otorgado.
          </p>
          <p>
            Asimismo, podrían recogerse datos de localización geográfica del dispositivo o terminal del Usuario, siempre y cuando haya otorgado su consentimiento para ello, con la finalidad de facilitar la prestación de servicios y ofrecerle información personalizada y adecuada a su ubicación. El Usuario podrá en cualquier momento desactivar el acceso a los datos de geolocalización, así como revocar el consentimiento prestado para su geolocalización, mediante la configuración de los ajustes de su dispositivo o terminal.
          </p>
        </q-tab-panel>
  
        <q-tab-panel name="sharing">
          <div class="text-h5 q-mb-md">5. CESIONES Y DESTINATARIOS DE LOS DATOS PERSONALES.</div>
          <p>
            Todas las cesiones de datos personales que realizará PADELPLAY resultan necesarias para el cumplimiento de las finalidades indicadas, o se realizan para cumplir una obligación legal, respecto de las siguientes Empresas y Organismos públicos:
          </p>
          <ul>
            <li>DESTINATARIO 1: Las Administraciones Públicas y la Organismo de Justicia.</li>
            <li>DESTINATARIO 2: Empresas y entidades colaboradoras de PADELPLAY, para la organización, gestión, y/o promoción de solicitudes, eventos o promociones, en caso de que el Usuario haya decidido inscribirse y/o formar parte de estos.</li>
            <li>DESTINATARIO 3: Sociedades prestadoras de servicios de solvencia patrimonial, crédito y prevención del fraude, para el análisis del riesgo y para el cotejo o contraste de sus datos a fin de comprobar la exactitud y veracidad de los mismos y a empresas proveedoras de Servicios de Pago.</li>
            <li>DESTINATARIO 4: Proveedores de PADELPLAY que, en su caso, sean contratados para medir el tráfico web, y el comportamiento de los usuarios por medio de cookies y sistemas similares, conforme a la Política de Cookies y que actuarán en condición de encargados del tratamiento.</li>
          </ul>
          <p>
            En relación con las anteriores comunicaciones, el Usuario cuenta con la posibilidad de obtener información acerca de con qué entidades concretas se mantienen acuerdos, en cada momento, que motivan dichas comunicaciones.
          </p>
          <p>
            Sin perjuicio de las comunicaciones de datos arriba indicadas, los datos personales del interesado podrán ser accedidos por terceros que presten servicios de administración u otros servicios (por ejemplo, administración, o servicios de seguridad) a PADELPLAY, así como soporte informático, mantenimiento u otro tipo de servicios de TI, y que deban tener acceso y tratar los datos personales por cuenta de PADELPLAY, actuando en calidad de encargados del tratamiento.
          </p>
        </q-tab-panel>
  
        <q-tab-panel name="protection">
          <div class="text-h5 q-mb-md">6. MEDIDAS ADOPTADAS PARA PROTEGER SUS DATOS</div>
          <p>
            Con el fin de garantizar la seguridad y confidencialidad de sus datos, PADELPLAY se compromete a tratar de forma absolutamente confidencial los datos de carácter personal del Usuario, haciendo uso de los mismos exclusivamente para las finalidades indicadas en esta política de privacidad. PADELPLAY ha adoptado los niveles de seguridad requeridos en materia de protección de datos y tiene implantadas las medidas de seguridad de índole técnica y organizativas necesarias que garantizan la seguridad de sus datos de personales y evitan su alteración, pérdida, tratamiento y/o acceso no autorizado, habida cuenta del estado de la tecnología, la naturaleza de los datos almacenados y los riesgos a que están expuestos, ya provengan de la acción humana o del medio físico o natural. En todo caso, debe tener en consideración que las medidas de seguridad en Internet no son inexpugnables.
          </p>
        </q-tab-panel>
  
        <q-tab-panel name="rights">
          <div class="text-h5 q-mb-md">7. ¿CUÁLES SON SUS DERECHOS?</div>
          <p>
            PADELPLAY le informa que tiene derecho a obtener confirmación sobre si estamos tratando datos personales que le conciernen o no. Del mismo modo, PADELPLAY le informa que usted cuenta con los siguientes derechos sobre sus datos de carácter personal:
          </p>
          <ul>
            <li>Acceder a sus datos. Ud. tiene derecho a acceder a sus datos para conocer qué datos personales estamos tratando que le conciernen.</li>
            <li>Solicitar la rectificación o supresión de sus datos. En determinadas circunstancias, Ud. tiene derecho a rectificar aquellos datos personales inexactos que le conciernen que sean objeto de tratamiento por nuestra parte o, incluso, a solicitarnos su supresión cuando, entre otros motivos, los datos ya no fueran necesarios para los fines que fueron recogidos.</li>
            <li>Asimismo, le recordamos que, en su caso, Ud. podrá oponerse al tratamiento de sus datos con fines promocionales.</li>
            <li>Derecho a no ser objeto de decisiones automatizadas. Tiene Ud. Derecho a no ser objeto de una decisión basada únicamente en el tratamiento automatizado, incluida la elaboración de perfiles, que produzca efectos jurídicos sobre Ud. o le afecte significativamente de modo similar.</li>
            <li>Los que se estipulan en las Leyes mexicanas y tratados Internacionales. </li>
          </ul>
          <p>
            Para el ejercicio de los citados derechos el interesado podrá ponerse en contacto dirigiendo un escrito a PADELPLAY a la dirección de correo electrónico jesus.gutierrez@padelplay.mx
          </p>
          <p>
            Responderemos a sus peticiones a la mayor brevedad posible y, en todo caso, en el plazo de un mes desde la recepción de su solicitud. Dicho plazo podrá prorrogarse otros dos meses en caso necesario, teniendo en cuenta la complejidad y el número de solicitudes. En tal caso, PADELPLAY informará al interesado de la prórroga dentro del primer mes desde la solicitud.
          </p>
          <p>
            En caso de modificaciones al presente Aviso de Privacidad, se informará mediante correo electrónico o aviso en la App, o nuestro sitio web oficial.
          </p>
        </q-tab-panel>
  
      </q-tab-panels>
    </q-page>
    </q-page-container>
    </q-layout>
  </template>
  
  <script>
  export default {
    data () {
      return {
        activeTab: 'responsible'
      }
    },
    methods: {
        goBack() {
      this.$router.back();
    },
    }
  }
  
  </script>

  <style scoped>
    .tabs {
        background-image: url("../../assets/texturafondo.png");
        background-size: cover;
    }

    .logo-icon {
    width: 60px; /* Ajusta el tamaño del logo */
    height: 60px;
    }
    .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000; /* Fondo del encabezado */
    } 
    .greeting {
    font-size: 1rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    }

    .header-icons {
    display: flex;
    gap: 2px;
    }
</style>