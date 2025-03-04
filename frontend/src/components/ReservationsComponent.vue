<template>
    <q-card class="tabs-section" v-if="days && days.length > 0">
      <q-card-section>
        <div class="q-mt-lg days-container">
          <q-btn flat icon="arrow_back" @click="previousWeek" />
          <div class="days-scroll">
            <q-btn
              v-for="(day, index) in days"
              :key="index"
              :outline="selectedDay !== day.date"
              color="grey"
              class="day-button"
              @click="selectDay(day.date)"
            >
              <div>{{ day.label }}</div>
              <div class="month-label">{{ day.month }}</div>
            </q-btn>
          </div>
          <q-btn flat icon="arrow_forward" @click="nextWeek" />
        </div>
        <div class="available-times q-mt-lg">
          <div v-if="loadingTimes === true" class="text-center">
            <q-spinner-dots color="white" size="xl" />
          </div>
          <div v-else-if="consolidatedTimes.length > 0" class="time-grid">
            <q-btn
              v-for="time in consolidatedTimes"
              :key="time"
              :label="time"
              :color="time === selectedTime ? 'green' : 'grey'"
              class="time-slot"
              @click="selectTime(time)"
            />
          </div>
          <div v-else class="text-center">
            No available times for the selected day.
          </div>
        </div>
        <div v-if="selectedTime" class="q-mt-lg">
          <h5>Canchas disponibles para {{ selectedTime }}:</h5>
          <div v-if="loadingCourts === true" class="text-center">
            <q-spinner-dots color="white" size="lg" />
          </div>
          <div v-else-if="availableCourts.length > 0">
            <q-list bordered separator>
              <q-expansion-item
                v-for="court in availableCourts"
                :key="court.id"
                expand-separator
                :label="court.name"
                :caption="`${court.is_indoor ? 'Techada' : 'Aire libre'}`"
                class="court-expansion-item"
              >
                <q-card class="court-card">
                  <q-card-section class="row q-gutter-sm justify-center">
                    <q-btn
                      v-for="option in timeOptions"
                      :key="option.duration"
                      color="primary"
                      @click="selectDuration(option, court)"
                      class="time-option-btn"
                    >
                      <div class="time-option-label">
                        <span>${{ getCourtPrice(court, option.duration) }}</span>
                        <br>
                        <span class="duration">{{ option.duration }} min</span>
                      </div>
                    </q-btn>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-list>
          </div>
          <div v-else class="text-center">
            No available courts for the selected time.
          </div>
        </div>
      </q-card-section>
    </q-card>
  </template>
  
  <script>
  export default {
    props: {
      days: { type: Array, default: () => [] },
      selectedDay: { type: String, default: "" },
      consolidatedTimes: { type: Array, default: () => [] },
      selectedTime: { type: String, default: "" },
      loadingTimes: { type: Boolean, default: false },
      availableCourts: { type: Array, default: () => [] },
      loadingCourts: { type: Boolean, default: false },
      timeOptions: { type: Array, default: () => [] },
    },
    data() {
      return {
        selectedCourt: null, // Ensure selected court is stored
      };
    },
    methods: {
      previousWeek() {
        this.$emit('previous-week');
      },
      nextWeek() {
        this.$emit('next-week');
      },
      selectDay(day) {
        this.$emit('select-day', day);
      },
      selectTime(time) {
        this.$emit('select-time', time || "");
      },
      selectDuration(option, court) {
        this.$emit('select-duration', { option, court }); // Ensure court is emitted
      },
      getCourtPrice(court, duration) {
        if (!court) return 0;
        if (duration === 60) {
          return court.price_per_hour || 0;
        } else if (duration === 90) {
          return court.price_per_hour_and_half || 0;
        } else if (duration === 120) {
          return court.price_per_two_hour || 0;
        }
        return 0;
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
  
  .time-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
    gap: 8px;
    justify-content: center;
  }
  
  .time-slot {
    text-align: center;
    font-size: 0.9rem;
    padding: 6px;
    height: 40px;
  }
  
  .day-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .month-label {
    font-size: 0.75rem;
    color: #aaa;
  }
  
  .days-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .days-scroll {
    display: flex;
    overflow-x: auto;
    flex-wrap: nowrap;
    gap: 8px;
  }
  
  .days-scroll::-webkit-scrollbar {
    display: none;
  }
  
  .court-expansion-item {
    background-color: #222;
    color: #fff;
  }
  
  .court-card {
    background-color: #222;
    padding: 10px;
    border-radius: 5px;
  }
  
  .time-option-btn {
    width: 88px;
    margin: 3px;
  }
  </style>
