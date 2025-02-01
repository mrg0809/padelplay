<template>
    <q-layout view="hHh lpR fFf" class="body text-black">
      <q-header elevated class="bg-primary text-white">
        <div class="header-content">
          <div class="greeting">
            <img src="/src/assets/padelplay.png" alt="Logo" class="logo-icon" />
            Gestión de Productos
          </div>
          <div class="header-icons">
            <q-btn flat round icon="close" @click="goBack" />
          </div>
        </div>
      </q-header>
  
      <q-page-container>
        <q-page class="q-pa-md">
          <!-- Tabla de productos -->
          <q-card class="transparent-card q-mb-md">
            <q-card-section>
              <div class="text-h6">Lista de Productos</div>
            </q-card-section>
            <q-card-section>
              <!-- Spinner mientras se cargan los datos -->
              <div v-if="loading" class="text-center q-pa-md">
                <q-spinner color="primary" size="xl" />
                <p class="q-mt-sm">Cargando productos...</p>
              </div>
  
              <!-- Mensaje si no hay productos -->
              <div v-else-if="products.length === 0" class="text-center q-pa-md">
                <q-icon name="o_shopping_cart" size="2em" />
                <p class="q-mt-sm">No hay productos registrados.</p>
              </div>
  
              <!-- Tabla si hay datos -->
              <q-table
                v-else
                :rows="products"
                :columns="columns"
                row-key="id"
                flat
                bordered
                class="transparent-table"
              >
                <!-- Columna personalizada para el botón de eliminar -->
                <template v-slot:body-cell-actions="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      round
                      color="negative"
                      icon="delete"
                      @click="deleteProduct(props.row.id)"
                    />
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
  
          <!-- Botón flotante para agregar producto -->
          <q-btn
            glossy
            round
            size="lg"
            color="black"
            icon="add"
            class="fixed-bottom-right q-mb-xl"
            @click="openProductDialog"
          />
  
          <!-- Diálogo para agregar producto -->
          <q-dialog v-model="isProductDialogOpen">
            <q-card class="bg-black text-white" style="min-width: 400px">
              <q-card-section>
                <div class="text-h6">Agregar Producto</div>
              </q-card-section>
  
              <q-card-section>
                <q-input
                  v-model="newProduct.name"
                  label="Nombre"
                  outlined
                  dense
                  color="white"
                />
                <q-input
                  v-model="newProduct.brand"
                  label="Marca"
                  outlined
                  dense
                  color="white"
                />
                <q-input
                  v-model="newProduct.category"
                  label="Familia/Categoría"
                  outlined
                  dense
                  color="white"
                />
                <q-input
                  v-model="newProduct.price"
                  label="Precio"
                  type="number"
                  outlined
                  dense
                  color="white"
                />
                <q-select
                    v-model="newProduct.modality"
                    :options="[{ label: 'Venta', value: 'sale' }, { label: 'Renta', value: 'rental' }]"
                    label="Modalidad"
                    outlined
                    dense
                    color="white"
                    emit-value
                    map-options
                />
              </q-card-section>
  
              <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="primary" v-close-popup />
                <q-btn flat label="Guardar" color="secondary" @click="saveProduct" />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </q-page>
      </q-page-container>
      <ClubNavigationMenu />
    </q-layout>
  </template>
  
  <script>
  import ClubNavigationMenu from "src/components/ClubNavigationMenu.vue";
  import api from "../../api";
  import { supabase } from "src/services/supabase";
  import { getUserFromToken } from "src/api";
  
  export default {
    data() {
      return {
        loading: false,
        isProductDialogOpen: false,
        products: [], // Lista de productos
        newProduct: {
          name: "",
          brand: "",
          category: "",
          price: 0,
          modality: "venta",
        },
        columns: [
          { name: "name", label: "Nombre", field: "name", align: "left" },
          { name: "brand", label: "Marca", field: "brand", align: "left" },
          { name: "category", label: "Categoría", field: "category", align: "left" },
          { name: "price", label: "Precio", field: "price", align: "left" },
          { name: "modality", label: "Modalidad", field: "modality", align: "left" },
          { name: "actions", label: "Acciones", field: "actions", align: "center" },
        ],
      };
    },
    components: {
      ClubNavigationMenu,
    },
    methods: {
      async fetchProducts() {
        this.loading = true;
        try {
          const user = getUserFromToken();
          if (!user || !user.club_id) {
            throw new Error("No se pudo obtener el club_id del usuario.");
          }
  
          const { data, error } = await supabase
            .from("club_products")
            .select("*")
            .eq("club_id", user.club_id);
  
          if (error) throw error;
  
          this.products = data;
        } catch (error) {
          console.error("Error al obtener los productos:", error);
          this.$q.notify({
            type: "negative",
            message: "Error al cargar los productos",
          });
        } finally {
          this.loading = false;
        }
      },
      openProductDialog() {
        this.isProductDialogOpen = true;
      },
      async saveProduct() {
        try {
          const user = getUserFromToken();
          if (!user || !user.club_id) {
            throw new Error("No se pudo obtener el club_id del usuario.");
          }
  
          const payload = {
            ...this.newProduct,
            club_id: user.club_id,
          };
  
          // Llamar al endpoint para guardar el producto
          await api.post("/products", payload);
  
          // Cerrar el diálogo y recargar la lista de productos
          this.isProductDialogOpen = false;
          await this.fetchProducts();
  
          // Mostrar notificación de éxito
          this.$q.notify({
            type: "positive",
            message: "Producto agregado exitosamente.",
          });
        } catch (error) {
          console.error("Error al guardar el producto:", error);
          this.$q.notify({
            type: "negative",
            message: "Error al guardar el producto. Intenta nuevamente.",
          });
        }
      },
      async deleteProduct(productId) {
        try {
          await api.delete(`/products/${productId}`);
          await this.fetchProducts();
          this.$q.notify({
            type: "positive",
            message: "Producto eliminado exitosamente.",
          });
        } catch (error) {
          console.error("Error al eliminar el producto:", error);
          this.$q.notify({
            type: "negative",
            message: "Error al eliminar el producto. Intenta nuevamente.",
          });
        }
      },
      goBack() {
        this.$router.back();
      },
    },
    mounted() {
      this.fetchProducts();
    },
  };
  </script>
  
  <style scoped>
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background-color: #000000;
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
  
  .logo-icon {
    width: 60px;
    height: 60px;
  }
  
  .body {
    background-image: url(../../assets/menu/padelcourtfloor.jpg);
    background-size: cover;
  }
  
  .fixed-bottom-right {
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 1000;
  }
  
  .transparent-card {
    background-color: rgba(255, 255, 255, 0.3);
  }
  
  .transparent-table {
    background-color: rgba(255, 255, 255, 0.3);
    color: black;
  }
  </style>