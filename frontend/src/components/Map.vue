<template>
  <div class="map-container">
    <div class="demo-title">
      <h1>人才流动地图</h1>
      <h3>展示各城市人才分布与流动情况</h3>
    </div>
    <div id="m-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const map = ref(null)
const locaContainer = ref(null)
const cityMarkers = ref([]) // 存储城市标记

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: "8459a6561ceacfac5ce2615f9b602d7e"
  }

  const loadAMap = () => {
    return new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://webapi.amap.com/maps?v=2.0&key=304e8147b61d6b38035924f4cd41237e'
      script.onload = () => resolve(window.AMap)
      document.body.appendChild(script)
    })
  }

  const loadLoca = () => {
    return new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://webapi.amap.com/loca?v=2.0.0&key=304e8147b61d6b38035924f4cd41237e'
      script.onload = () => resolve(window.Loca)
      document.body.appendChild(script)
    })
  }

  loadAMap().then((AMap) => {
    loadLoca().then((Loca) => {
      initMap(AMap, Loca)
    })
  })
})

const initMap = (AMap, Loca) => {
  map.value = new AMap.Map("m-container", {
    zooms: [4, 7],
    zoom: 4.75,
    center: [102.618687, 31.790976],
    showLabel: false,
    viewMode: '3D',
    mapStyle: 'amap://styles/45311ae996a8bea0da10ad5151f72979',
    pitch: 40,
  })

  locaContainer.value = new Loca.Container({
    map: map.value
  })

  fetchCityData(AMap, Loca)
}

const fetchCityData = (AMap, Loca) => {
  axios.get('/api/cities')
      .then(response => {
        const cityData = response.data;
        if (Array.isArray(cityData)) {
          const geoJsonData = convertToGeoJSON(cityData);
          createHeatMap(geoJsonData, Loca);
          addCityLabels(cityData, AMap); // 添加城市名称标注
        }
      })
      .catch(error => {
        console.error('获取城市数据失败:', error);
      });
};

const convertToGeoJSON = (cities) => ({
  type: "FeatureCollection",
  features: cities.map(city => ({
    type: "Feature",
    geometry: {
      type: "Point",
      coordinates: [city.longitude, city.latitude]
    },
    properties: {
      count: city.count,
      city: city.city_name
    }
  }))
});

const createHeatMap = (geoJsonData, Loca) => {
  const geoSource = new Loca.GeoJSONSource({ data: geoJsonData });

  const heatmap = new Loca.HeatMapLayer({
    zIndex: 10,
    opacity: 0.8,
    visible: true,
    zooms: [2, 22],
  });

  heatmap.setSource(geoSource, {
    radius: 200000,
    unit: 'meter',
    height: 500000,
    gradient: {
      0.1: '#2A85B8',
      0.2: '#16B0A9',
      0.3: '#29CF6F',
      0.4: '#5CE182',
      0.5: '#7DF675',
      0.6: '#FFF100',
      0.7: '#FAA53F',
      1: '#D04343'
    },
    value: (index, feature) => feature.properties.count,
    heightBezier: [0, .53, .37, .98]
  });

  locaContainer.value.add(heatmap);

  map.value.on('complete', () => {
    heatmap.addAnimate({
      key: 'height',
      value: [0, 1],
      duration: 2000,
      easing: 'BackOut'
    });
  });
};

// 简化的城市名称标注：仅显示城市名
const addCityLabels = (cities, AMap) => {
  cities.forEach(city => {
    const text = new AMap.Text({
      text: city.city_name,
      position: [city.longitude, city.latitude],
      offset: new AMap.Pixel(-15, -10), // 微调位置，使文本居中显示
      style: {
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
        color: '#333',
        fontSize: '10px',
        padding: '2px 6px',
        borderRadius: '3px',
        whiteSpace: 'nowrap',
        border: 'none', // 移除边框
        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)' // 添加轻微阴影
      },
      zIndex: 20 // 确保在热力图上方
    });

    text.setMap(map.value);
    cityMarkers.value.push(text); // 存储文本标签
  });
};
</script>

<style scoped>
#m-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}

.demo-title {
  position: absolute;
  top: 25px;
  left: 25px;
  z-index: 100;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 12px 18px;
  border-radius: 6px;
}

h1 {
  font-size: 20px;
  margin: 0;
  color: white;
  font-weight: 500;
}

h3 {
  font-size: 14px;
  margin-top: 6px;
  color: #e0e0e0;
  font-weight: 400;
}

</style>