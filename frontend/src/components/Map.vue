<template>
  <div class="map-container">
    <!-- 左侧：人才详细信息 -->
    <div class="talent-detail" v-if="selectedTalent">
      <h2>{{ selectedTalent.authfull }}</h2>
      <div class="detail-content">
        <p><strong>机构：</strong>{{ selectedTalent.instName || '未知' }}</p>
        <p><strong>国家：</strong>{{ selectedTalent.cntry || '未知' }}</p>
        <p><strong>研究领域：</strong>{{ getResearchField(selectedTalent) }}</p>
        <p><strong>总体排名：</strong>{{ selectedTalent.rankAll || '未排名' }}</p>
        <p><strong>h指数(所有领域)：</strong>{{ selectedTalent.h23All || 0 }}</p>
        <p><strong>论文数量：</strong>{{ selectedTalent.np6023 || 0 }}</p>
        <p><strong>引用次数：</strong>{{ selectedTalent.npcitingAll || 0 }}</p>
        <p><strong>首次发表年份：</strong>{{ selectedTalent.firstYear || '未知' }}</p>
        <p><strong>最后发表年份：</strong>{{ selectedTalent.lastYear || '未知' }}</p>
      </div>
      <button @click="closeDetail">关闭</button>
    </div>

    <!-- 主地图区域 -->
    <div id="m-container"></div>

<!--    &lt;!&ndash; 顶部标题 &ndash;&gt;-->
<!--    <div class="demo-title">-->
<!--      <h1>人才流动地图</h1>-->
<!--      <h3>点击国家标签查看人才分布（最多显示100人）</h3>-->
<!--    </div>-->

    <!-- 右侧：人才列表（分页） -->
    <div class="talent-list" v-if="currentCountry.name">
      <div class="list-header">
        <h2>{{ currentCountry.name }} 人才列表</h2>
        <p>共 {{ totalTalents }} 人</p>
      </div>

      <div class="talent-items">
        <div
            class="talent-item"
            v-for="(talent, index) in talentList"
            :key="talent.id"
            @click="showTalentDetail(talent)"
            >
          <div class="talent-basic">
            <span class="rank">{{ (currentPage - 1) * 10 + index + 1 }}</span>
            <span class="name">{{ talent.authfull }}</span>
          </div>
          <div class="talent-info">
            <span>{{ getResearchField(talent) }}</span>
            <span>排名: {{ talent.rankAll || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- 分页控件 -->
      <div class="pagination">
        <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage <= 1"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
        </span>
        <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import axios from 'axios'

// 状态管理
const map = ref(null)
const locaContainer = ref(null)
const countryMarkers = ref([]) // 存储国家标签
const talentLayers = ref([]) // 存储人才点图层
const currentCountry = reactive({
  name: '',
  code: '',
  lng: 0,
  lat: 0
})

// 新增状态：人才列表和分页
const talentList = ref([])
const selectedTalent = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const totalTalents = ref(0)


// 计算属性：总页数
const totalPages = computed(() => {
  return Math.ceil(totalTalents.value / pageSize.value) || 1
})

// 初始化地图
onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: "8459a6561ceacfac5ce2615f9b602d7e"
  }

  // 加载高德地图SDK
  const loadAMap = () => new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=304e8147b61d6b38035924f4cd41237e'
    script.onload = () => resolve(window.AMap)
    document.body.appendChild(script)
  })

  // 加载Loca可视化库
  const loadLoca = () => new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/loca?v=2.0.0&key=304e8147b61d6b38035924f4cd41237e'
    script.onload = () => resolve(window.Loca)
    document.body.appendChild(script)
  })

  // 初始化地图
  loadAMap().then((AMap: any) => {
    loadLoca().then((Loca: any) => {
      initMap(AMap, Loca)
    })
  })
})

// 初始化地图实例
const initMap = (AMap: any, Loca: any) => {
  map.value = new AMap.Map("m-container", {
    zooms: [2, 7],
    zoom: 2.5,
    center: [0, 20],
    showLabel: false,
    viewMode: '3D',
    mapStyle: 'amap://styles/45311ae996a8bea0da10ad5151f72979',
    pitch: 30,
  })

  locaContainer.value = new Loca.Container({ map: map.value })
  fetchCountryData(AMap, Loca)
}

// 获取国家数据
const fetchCountryData = (AMap: any, Loca: any) => {
  axios.get('/api/countries')
      .then(response => {
        const countryData = response.data;
        if (Array.isArray(countryData)) {
          const geoJsonData = convertToGeoJSON(countryData);
          createHeatMap(geoJsonData, Loca);
          addCountryLabels(countryData, AMap);
        }
      })
      .catch(error => {
        console.error('获取国家数据失败:', error);
      });
};

// 转换为GeoJSON
const convertToGeoJSON = (countries: any[]) => ({
  type: "FeatureCollection",
  features: countries.map(country => ({
    type: "Feature",
    geometry: {
      type: "Point",
      coordinates: [country.longitude, country.latitude]
    },
    properties: {
      count: country.count,
      country: country.country
    }
  }))
})

// 创建热力图
const createHeatMap = (geoJsonData: any, Loca: any) => {
  const geoSource = new Loca.GeoJSONSource({ data: geoJsonData });

  const heatmap = new Loca.HeatMapLayer({
    zIndex: 10,
    opacity: 0.8,
    visible: true,
    zooms: [2, 22],
  });

  heatmap.setSource(geoSource, {
    radius: 1000000,
    unit: 'meter',
    height: 1000000,
    minHeight: 50000,
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
    value: (index: number, feature: any) => Math.log(feature.properties.count + 1),
    heightBezier: [0, 0.3, 0.7, 1]
  });

  locaContainer.value.add(heatmap);
};

// 添加国家标签（带点击和悬停事件）
const addCountryLabels = (countries: any[], AMap: any) => {
  // 先清除旧标签
  countryMarkers.value.forEach(marker => marker.remove());
  countryMarkers.value = [];

  countries.forEach(country => {
    // 创建可点击的国家标签
    const text = new AMap.Text({
      text: country.country,
      position: [country.longitude, country.latitude],
      offset: new AMap.Pixel(-20, -15),
      style: {
        backgroundColor: 'rgba(255, 255, 255, 0.25)',
        color: '#333',
        fontSize: '12px',
        padding: '3px 8px',
        borderRadius: '4px',
        cursor: 'pointer',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)',
        transition: 'all 0.3s ease'
      },
      zIndex: 20
    });

    // 悬停效果
    text.on('mouseover', () => {
      text.setStyle({
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        color: '#000',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
      });
    });

    // 鼠标离开效果
    text.on('mouseout', () => {
      if (!(currentCountry.code === country.cntry)) {
        text.setStyle({
          backgroundColor: 'rgba(255, 255, 255, 0.25)',
          color: '#333',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)'
        });
      }
    });

    // 绑定点击事件
    text.on('click', () => {
      currentCountry.name = country.country;
      currentCountry.code = country.cntry;
      currentCountry.lng = country.longitude;
      currentCountry.lat = country.latitude;

      // 更新标签样式
      countryMarkers.value.forEach(marker => {
        if (marker.getContent() === country.country) {
          marker.setStyle({
            backgroundColor: 'rgba(255, 255, 0, 0.8)',
            color: '#000',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
          });
        } else {
          marker.setStyle({
            backgroundColor: 'rgba(255, 255, 255, 0.25)',
            color: '#333',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)'
          });
        }
      });

      handleCountryClick(country.country, country.cntry, country.longitude, country.latitude);
    });

    text.setMap(map.value);
    countryMarkers.value.push(text);
  });
};

// 处理国家点击事件
const handleCountryClick = (countryName: string, countryCode: string, centerLng: number, centerLat: number) => {
  console.log(`点击了${countryName}，代码：${countryCode}`);

  // 清除上一次的人才标记
  clearTalentMarkers();
  // 重置分页
  currentPage.value = 1;
  // 清空选中的人才
  selectedTalent.value = null;

  // 调用后端接口获取分页数据
  fetchTalentsByCountry(countryCode);

  // 创建地图上的人才标记点
  axios.get(`/api/talentPerson/country/${countryCode}`)
      .then(response => {
        const talents = response.data;
        if (Array.isArray(talents) && talents.length > 0) {
          createTalentMarkers(talents, centerLng, centerLat);
        } else {
          console.log(`该国家暂无人才数据`);
        }
      })
      .catch(error => {
        console.error(`获取${countryName}人才数据失败:`, error);
      });
};

// 获取国家人才列表（带分页）
const fetchTalentsByCountry = (countryCode: string) => {
  axios.get(`/api/talentPerson/country/${countryCode}/page/${currentPage.value}?size=${pageSize.value}`)
      .then(response => {
        const data = response.data;
        console.log('分页数据：', data); // 打印总条数、当前页内容
        talentList.value = data.content;
        totalTalents.value = data.totalElements;
      })
      .catch(error => {
        console.error(`获取人才分页数据失败:`, error);
      });
};

// 切换分页
const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchTalentsByCountry(currentCountry.code);

  // 滚动到顶部
  const listElement = document.querySelector('.talent-list');
  if (listElement) {
    listElement.scrollTop = 0;
  }
};

// 查看人才详情
const showTalentDetail = (talent: any) => {
  selectedTalent.value = talent;
};

// 关闭详情
const closeDetail = () => {
  selectedTalent.value = null;
};

// 生成圆形分布的人才标记点
const createTalentMarkers = (talents: any[], centerLng: number, centerLat: number) => {
  if (!locaContainer.value) {
    console.error('Loca容器未初始化');
    return;
  }

  // 1. 限制最大显示数量
  const maxDisplayCount = 100;
  const displayTalents = talents.slice(0, maxDisplayCount);

  // 2. 准备GeoJSON数据（使用圆形分布算法）
  const talentGeoJson = {
    type: "FeatureCollection",
    features: displayTalents.map((talent, index) => {
      // 配置圆形分布半径（单位：度）
      const radius = 1; // 可调整大小（1度≈111公里）

      // 圆形分布算法：通过极坐标转换实现
      const randomRadius = Math.sqrt(Math.random()) * radius;
      const randomAngle = Math.random() * 2 * Math.PI;

      // 极坐标转直角坐标（计算偏移量）
      const randomLng = randomRadius * Math.cos(randomAngle);
      const randomLat = randomRadius * Math.sin(randomAngle);

      // 最终坐标
      const finalLng = centerLng + randomLng;
      const finalLat = centerLat + randomLat;

      return {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [finalLng, finalLat]
        },
        properties: {
          id: talent.id,
          name: talent.authfull,
          institution: talent.instName || '未知机构'
        }
      };
    })
  };

  // 3. 创建散点图层
  const talentSource = new (window as any).Loca.GeoJSONSource({
    data: talentGeoJson
  });

  const scatterLayer = new (window as any).Loca.ScatterLayer({
    zIndex: 30,
    opacity: 1,
    visible: true,
    zooms: [2, 22]
  });

  scatterLayer.setSource(talentSource, {
    unit: 'px',
    size: [20, 20],
    texture: 'https://a.amap.com/Loca/static/loca-v2/demos/images/blue.png',
    borderWidth: 0,
    select: {
      enable: true,
      mode: 'single',
      style: {
        size: [25, 25]
      }
    }
  });

  // 点击地图上的人才点显示详情
  scatterLayer.on('select', (e: any) => {
    if (e.feature) {
      const talentId = e.feature.properties.id;
      // 在列表中找到对应的人才
      const talent = talentList.value.find(t => t.id === talentId) ||
          talentList.value.find(t => t.authfull === e.feature.properties.name);
      if (talent) {
        selectedTalent.value = talent;
      }
    }
  });

  // 4. 添加呼吸效果图层
  const topTalents = talentGeoJson.features.slice(0, 10);
  if (topTalents.length > 0) {
    const breathSource = new (window as any).Loca.GeoJSONSource({
      data: {
        type: "FeatureCollection",
        features: topTalents
      }
    });

    const breathLayer = new (window as any).Loca.ScatterLayer({
      zIndex: 29,
      opacity: 0.8
    });

    breathLayer.setSource(breathSource, {
      unit: 'px',
      size: [50, 50],
      texture: 'https://a.amap.com/Loca/static/loca-v2/demos/images/breath_red.png',
      animate: true,
      duration: 1000
    });

    locaContainer.value.add(breathLayer);
    talentLayers.value.push(breathLayer);
  }

  // 5. 添加到地图
  locaContainer.value.add(scatterLayer);
  talentLayers.value.push(scatterLayer);

  // 6. 开始动画
  locaContainer.value.animate.start();
};

// 清除人才标记
const clearTalentMarkers = () => {
  if (!locaContainer.value) {
    return;
  }

  talentLayers.value.forEach(layer => {
    locaContainer.value.remove(layer);
  });
  talentLayers.value = [];
};

// 辅助函数：获取研究领域
const getResearchField = (talent: any) => {
  const fields = [];
  if (talent.smField) fields.push(talent.smField);
  if (talent.smSubfield1) fields.push(talent.smSubfield1);
  return fields.length > 0 ? fields.join(' / ') : '未知';
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

/* 右侧人才列表样式 */
.talent-list {
  position: absolute;
  top: 0;
  right: 0;
  width: 380px;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 100;
  overflow-y: auto;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  box-sizing: border-box;
}

.list-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.list-header h2 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.list-header p {
  margin: 5px 0 0;
  color: #666;
  font-size: 14px;
}

.talent-item {
  padding: 12px;
  border-radius: 8px;
  background-color: #f9f9f9;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.talent-item:hover {
  background-color: #f0f7ff;
  border-left-color: #2A85B8;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.talent-item.selected {
  background-color: #e6f7ff;
  border-left-color: #1890ff;
}

.talent-basic {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.rank {
  background-color: #2A85B8;
  color: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 10px;
  flex-shrink: 0;
}

.name {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.talent-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

/* 分页样式 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  padding: 15px 0;
  border-top: 1px solid #eee;
}

.pagination button {
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 5px;
}

.pagination button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pagination button:hover:not(:disabled) {
  background-color: #e9e9e9;
}

.page-info {
  margin: 0 10px;
  color: #666;
  font-size: 14px;
}

/* 左侧人才详情样式 */
.talent-detail {
  position: absolute;
  top: 0;
  left: 0;
  width: 380px;
  height: 100vh;
  background-color: white;
  z-index: 100;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  box-sizing: border-box;
}

.talent-detail h2 {
  margin-top: 0;
  color: #333;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #555;
}

.detail-content strong {
  color: #333;
}

.talent-detail button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #2A85B8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.talent-detail button:hover {
  background-color: #1f6d9a;
}

.info-popup {
  position: absolute;
  background-color: white;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 100;
  font-size: 12px;
  max-width: 200px;
}
</style>