<template>
    <q-card class="tabs-section">
      <q-card-section>
        <p><strong>Dirección:</strong> {{ clubDetails?.address || "No disponible" }}</p>
        <p v-if="clubDetails?.city"><strong>Ciudad:</strong> {{ clubDetails.city }}, {{ clubDetails.state }}, {{ clubDetails.country }}</p>
        <div id="map" style="height: 200px;" v-if="coordinates"></div>
        <div v-if="clubDetails">
          <div class="q-mt-md text-center">
            <q-btn
              v-if="coordinates"
              flat
              round
              icon="mdi-google-maps"
              color="blue"
              class="q-my-md"
              size="xl"
              @click="openMaps(coordinates)"
            />
            <q-btn
              v-if="clubDetails.facebook_url"
              flat
              round
              icon="mdi-facebook"
              color="blue"
              class="q-mx-sm"
              size="xl"
              @click="openSocialLink(clubDetails.facebook_url)"
            />
            <q-btn
              v-if="clubDetails.instagram_url"
              flat
              round
              icon="mdi-instagram"
              color="purple"
              class="q-mx-sm"
              size="xl"
              @click="openSocialLink(clubDetails.instagram_url)"
            />
            <q-btn
              v-if="clubDetails.tiktok_url"
              flat
              round
              icon="mdi-tiktok"
              color="white"
              class="q-mx-sm"
              size="xl"
              @click="openSocialLink(clubDetails.tiktok_url)"
            />
            <q-btn
              v-if="clubDetails.whatsapp_number"
              flat
              round
              icon="mdi-whatsapp"
              color="green"
              class="q-mx-sm"
              size="xl"
              @click="openWhatsApp(clubDetails.whatsapp_number)"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </template>
  
  <script>
  export default {
    props: {
      clubDetails: Object,
      coordinates: Object,
    },
    methods: {
      openMaps(coordinates) {
        const mapsUrl = `https://www.google.com/maps?q=${coordinates.lat},${coordinates.lng}`;
        window.open(mapsUrl, "_blank");
      },
      openSocialLink(url) {
        if (url) {
          window.open(url, "_blank");
        }
      },
      openWhatsApp(number) {
        if (number) {
          const whatsappUrl = `https://wa.me/${number}`;
          window.open(whatsappUrl, "_blank");
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .tabs-section {
    margin-bottom: 10px;
    background-image: url(src/assets/texturafondo.png);
    background-size: cover;
    border-radius: 20px;
  }
  </style>