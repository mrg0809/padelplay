<template>
  <q-card class="tabs-section">
    <q-card-section>
      <p><strong>Dirección:</strong> {{ clubDetails?.address || "No disponible" }}</p>
      <p v-if="clubDetails?.city">
        <strong>Ciudad:</strong> {{ clubDetails.city }}, {{ clubDetails.state }}, {{ clubDetails.country }}
      </p>

      <div id="map" style="height: 200px;" v-if="coordinates"></div>

      <div v-if="clubDetails" class="q-mt-md text-center">
        <q-btn
          v-if="coordinates"
          flat round size="xl"
          icon="mdi-google-maps"
          color="blue"
          class="q-mx-sm"
          @click="openMaps(coordinates)"
        />
        <q-btn
          v-if="clubDetails.facebook_url"
          flat round size="xl"
          icon="mdi-facebook"
          color="blue"
          class="q-mx-sm"
          @click="openSocialLink(clubDetails.facebook_url)"
        />
        <q-btn
          v-if="clubDetails.instagram_url"
          flat round size="xl"
          icon="mdi-instagram"
          color="purple"
          class="q-mx-sm"
          @click="openSocialLink(clubDetails.instagram_url)"
        />
        <q-btn
          v-if="clubDetails.tiktok_url"
          flat round size="xl"
          icon="mdi-tiktok"
          color="white"
          class="q-mx-sm"
          @click="openSocialLink(clubDetails.tiktok_url)"
        />
        <q-btn
          v-if="clubDetails.whatsapp_number"
          flat round size="xl"
          icon="mdi-whatsapp"
          color="green"
          class="q-mx-sm"
          @click="openWhatsApp(clubDetails.whatsapp_number)"
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { defineProps } from "vue";
import { openMaps, openSocialLink, openWhatsApp } from "../helpers/clubUtils";

defineProps({
  clubDetails: Object,
  coordinates: Object,
});
</script>

<style scoped>
.tabs-section {
  margin-bottom: 10px;
  background-image: url(src/assets/texturafondo.png);
  background-size: cover;
  border-radius: 20px;
}
</style>
