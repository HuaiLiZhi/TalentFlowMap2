<template>
  <div class="map-container">
    <!-- 左侧人员信息侧边栏（增加显示控制） -->
    <div class="person-sidebar" v-if="showPersonSidebar">
      <div class="sidebar-header">
        <div class="header-content">
          <h3>
            {{ selectedProvince ? `${selectedProvince.name} 人员信息` : '请选择省份' }}
          </h3>
          <button class="close-btn" @click="showPersonSidebar = false">×</button>
        </div>
        <p class="year-indicator">当前年份: {{ selectedYear }}</p>
      </div>
      <div class="person-list">
        <div v-if="filteredPersons.length === 0" class="empty提示">
          暂无该省份在{{ selectedYear }}年的人员数据
        </div>

        <div v-for="person in filteredPersons" :key="person.person_id" class="person-card"
          @click="selectPerson(person)">
          <!-- 人员卡片内容保持不变 -->
          <div class="person-header">
            <h4>{{ person.name }}</h4>
            <span class="industry-tag">{{ person.industry }}</span>
          </div>
          <div class="person-info">
            <div class="info-row">
              <p>ID: {{ person.person_id }}</p>
              <p>职位: {{ person.position }}</p>
            </div>
            <div class="info-row">
              <p>工作年限: {{ person.work_years }}年</p>
            </div>
          </div>
          <div class="abilities">
            <div class="ability-row">
              <div class="ability-item">
                <span>基础能力: {{ person.basic_ability }}</span>
              </div>
              <div class="ability-item">
                <span>专业能力: {{ person.professional_ability }}</span>
              </div>
            </div>
            <div class="ability-row">
              <div class="ability-item">
                <span>创新能力: {{ person.innovative_ability }}</span>
              </div>
              <div class="ability-item">
                <span>综合评分: {{ person.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 人员详细信息显示框（增加显示控制） -->
    <div class="person-detail-panel" v-if="showPersonDetail && selectedPerson">
      <div class="detail-header">
        <h3>人员详细信息</h3>
        <button class="close-btn" @click="showPersonDetail = false">×</button>
      </div>
      <div class="detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="two-column">
            <p>姓名: {{ selectedPerson.name }}</p>
            <p>ID: {{ selectedPerson.person_id }}</p>
            <p>性别: {{ selectedPerson.sex }}</p>
            <p>年龄: {{ selectedPerson.age }}岁</p>
            <p>籍贯: {{ selectedPerson.native_place }}</p>
          </div>
        </div>

        <!-- 教育背景 -->
        <div class="detail-section">
          <h4>教育背景</h4>
          <div class="two-column">
            <p>最高学历: {{ selectedPerson.highest_education }}</p>
            <p>毕业院校: {{ selectedPerson.graduated_school }}</p>
          </div>
        </div>

        <!-- 工作信息 -->
        <div class="detail-section">
          <h4>工作信息</h4>
          <div class="two-column">
            <p>行业: {{ selectedPerson.industry }}</p>
            <p>职位: {{ selectedPerson.position }}</p>
            <p>工作年限: {{ selectedPerson.work_years }}年</p>
          </div>
        </div>

        <!-- 能力评估 -->
        <div class="detail-section">
          <h4>能力评估</h4>
          <div class="two-column">
            <p>综合评分: {{ selectedPerson.score }}</p>
            <p>基础能力: {{ selectedPerson.basic_ability }}</p>
            <p>专业能力: {{ selectedPerson.professional_ability }}</p>
            <p>创新能力: {{ selectedPerson.innovative_ability }}</p>
          </div>

          <!-- 雷达图容器 -->
          <div class="radar-chart-container">
            <div ref="radarChart" class="radar-chart"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地图容器 -->
    <div id="m-container"></div>

    <!-- 右侧控制面板（仅保留省市选择） -->
    <!-- <div class="control-panel province-panel">
      <h3>中国省市选择</h3>
      <div class="province-list">
        <div v-for="province in provinces" :key="province.adcode"
          :class="{ 'province-item': true, 'active': activeProvince === province.adcode }"
          @click="selectProvince(province)">
          {{ province.name }}
        </div>
      </div>
    </div> -->

    <!-- 时间轴组件 -->
    <div class="timeline-container">
      <div class="timeline-header">
        <span class="timeline-title">年份选择</span>
        <div class="timeline-track">
          <div v-for="year in years" :key="year" :class="{ 'timeline-item': true, 'active': selectedYear === year }"
            @click="handleYearClick(year)">
            {{ year }}
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧控制面板（新增人才数据统计面板） -->
    <div v-if="showTalentPanel" class="control-panel talent-panel">
      <div class="panel-header">
        <h3>人才数据统计</h3>
        <button class="close-btn" @click="showTalentPanel = false">×</button>
      </div>

      <!-- 人才数量变化折线图 -->
      <!-- <div class="chart-section">
        <h4>人才数量变化趋势</h4>
        <div id="cline" ref="talentTrendChart" class="small-chart">
        </div>
      </div> -->

      <!-- 人才流入Top5 -->
      <div class="stat-table">
        <h4>主要人才来源 (Top5)</h4>
        <div v-if="incomingTop5.length === 0" class="empty-stat">暂无数据</div>
        <div v-else class="stat-row" v-for="(item, index) in incomingTop5" :key="'in-' + index">
          <span class="rank">{{ index + 1 }}</span>
          <span class="province-name">{{ item.province }}</span>
          <span class="count">{{ item.count }}人</span>
        </div>
      </div>

      <!-- 人才流出Top5 -->
      <div class="stat-table">
        <h4>主要人才去向 (Top5)</h4>
        <div v-if="outgoingTop5.length === 0" class="empty-stat">暂无数据</div>
        <div v-else class="stat-row" v-for="(item, index) in outgoingTop5" :key="'out-' + index">
          <span class="rank">{{ index + 1 }}</span>
          <span class="province-name">{{ item.province }}</span>
          <span class="count">{{ item.count }}人</span>
        </div>
      </div>
    </div>

    <!-- 新增：显示统计面板的按钮 -->
    <button v-if="!showTalentPanel && selectedProvince" class="show-talent-btn" @click="showTalentPanel = true">
      显示人才统计
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted, nextTick } from 'vue'
import provincesData from './json/china-provinces.json'
import populationData from './json/data/province_population_frequency.json'
import traceData from './json/data/province_migration_frequency.json'
import personData from './json/data/persons_track.json'
import personDetailData from './json/data/persons_info.json'

import * as echarts from 'echarts'

// 定义数据
const provinces = ref(provincesData.provinces)
const selectedProvince = ref(null)
const activeProvince = ref('')
const map = ref(null)
const textOverlays = ref([])
const circleOverlays = ref([])

// 时间轴相关
const years = ref<number[]>([])
const selectedYear = ref<number>(0)
const yearGroupData = ref<Record<number, Record<string, any>>>({})

// 轨迹线相关
const traceLines = ref([])
const yearTraceData = ref({})
// 新增：人员轨迹线存储
const personTraceLines = ref([])
const personTraceLabels = ref([])

// 人员数据相关
const personTracks = ref(personData)
const yearProvincePersons = ref<Record<number, Record<string, any[]>>>({})
const filteredPersons = ref([])

// 人员详细信息相关
const personDetails = ref(personDetailData)
const selectedPerson = ref(null)
const showPersonSidebar = ref(true)
const showPersonDetail = ref(true)

// 雷达图相关
const radarChart = ref<HTMLDivElement>(null)
const chartInstance = ref<echarts.ECharts | null>(null)

// 新增：人才统计相关数据
const talentTrendChart = ref<HTMLDivElement>(null)
const trendChartInstance = ref<echarts.ECharts | null>(null)
const incomingTop5 = ref([])
const outgoingTop5 = ref([])
const talentCountByYear = ref<Record<number, number>>({})

const showTalentPanel = ref(false);

const initTalentTrendChart = () => {
  if (talentTrendChart.value) {
    trendChartInstance.value = echarts.init(talentTrendChart.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '人才数量'
      },
      series: [
        {
          name: '人才数量',
          type: 'line',
          data: [],
          smooth: true,
          lineStyle: {
            width: 3
          },
          itemStyle: {
            radius: 6
          }
        }
      ]
    }

    trendChartInstance.value.setOption(option)
  }
}

// 更新人才趋势图表数据
const updateTalentTrendChart = () => {
  if (trendChartInstance.value && Object.keys(talentCountByYear.value).length > 0) {
    // 按年份排序
    const sortedYears = Object.keys(talentCountByYear.value)
      .map(Number)
      .sort((a, b) => a - b)

    const counts = sortedYears.map(year => talentCountByYear.value[year])

    trendChartInstance.value.setOption({
      xAxis: {
        data: sortedYears.map(String)
      },
      series: [
        {
          data: counts
        }
      ]
    })
  }
}

// 计算选中省份的人才统计数据
const calculateTalentStats = (provinceName: string) => {
  // 1. 计算各年份人才数量
  const countByYear: Record<number, number> = {}
  years.value.forEach(year => {
    const provincePersons = yearProvincePersons.value[year]?.[provinceName] || []
    // 使用Set确保每个ID只计数一次
    const uniqueIds = new Set(provincePersons.map(p => p.person_id))
    countByYear[year] = uniqueIds.size
  })
  talentCountByYear.value = countByYear

  // 2. 计算人才流入Top5（其他省份到当前省份）
  const incomingMap: Record<string, number> = {}
  // 3. 计算人才流出Top5（当前省份到其他省份）
  const outgoingMap: Record<string, number> = {}

  // 遍历所有迁移数据
  // console.log('计算人才流入和流出数据...')
  // console.log(yearTraceData.value)
  Object.values(yearTraceData.value).forEach(yearData => {
    yearData.forEach(trace => {
      // 人才流入：其他省份到当前省份

      if (trace.end_province === provinceName && trace.start_province !== provinceName) {
        // console.log(`处理迁移数据: ${trace.start_province} -> ${trace.end_province}, 频率: ${trace.frequency}, 人数： ${trace.population}`)
        incomingMap[trace.start_province] = (incomingMap[trace.start_province] || 0) + trace.population
      }

      // 人才流出：当前省份到其他省份
      if (trace.start_province === provinceName && trace.end_province !== provinceName) {
        outgoingMap[trace.end_province] = (outgoingMap[trace.end_province] || 0) + trace.population
      }
    })
  })
  // 转换为数组并排序，取前5
  incomingTop5.value = Object.entries(incomingMap)
    .map(([province, count]) => ({ province, count: Math.round(count) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)

  outgoingTop5.value = Object.entries(outgoingMap)
    .map(([province, count]) => ({ province, count: Math.round(count) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)

  // 更新图表
  updateTalentTrendChart()
}

// 在选择省份时计算统计数据
watch(() => selectedProvince.value, (newProvince) => {
  if (newProvince) {
    nextTick(() => {
      calculateTalentStats(newProvince.name);
      // 可选：选择省份时自动显示统计面板
      showTalentPanel.value = true;
    });
  }
});


// 转换学历为数值（用于雷达图）
const getEducationValue = (education: string) => {
  switch (education) {
    case '博士': return 2;
    case '硕士': return 1;
    default: return 0; // 其他学历（如本科）
  }
}

// 初始化雷达图
const initRadarChart = () => {
  if (radarChart.value) {
    chartInstance.value = echarts.init(radarChart.value)

    // 设置雷达图配置
    const option = {
      tooltip: {
        trigger: 'item'
      },
      radar: {
        indicator: [
          { name: '工作年限', max: 30 }, // 假设最大30年
          { name: '最高学历', max: 2 }, // 博士=2，硕士=1
          { name: '基础能力', max: 5 },
          { name: '专业能力', max: 5 },
          { name: '创新能力', max: 5 }
        ],
        splitArea: {
          areaStyle: {
            color: ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.2)']
          }
        }
      },
      series: [
        {
          name: '能力数据',
          type: 'radar',
          symbolSize: 6,
          lineStyle: {
            width: 2
          },
          areaStyle: {
            opacity: 0.3
          },
          data: []
        }
      ]
    }

    chartInstance.value.setOption(option)
  }
}

// 更新雷达图数据
const updateRadarData = (person) => {
  if (!person) return;
  nextTick(() => {
    // 若图表未初始化，先初始化再更新
    if (!chartInstance.value && radarChart.value) {
      initRadarChart();
    }
    if (chartInstance.value) {
      const radarData = [
        {
          value: [
            Number(person.work_years) || 0, // 强制转为数字，避免非数值类型
            getEducationValue(person.highest_education || ''),
            Number(person.basic_ability) || 0,
            Number(person.professional_ability) || 0,
            Number(person.innovative_ability) || 0
          ],
          name: person.name || '人员'
        }
      ];
      chartInstance.value.setOption({ series: [{ data: radarData }] });
    }
  });
};

// 监听人员选择变化，更新雷达图
watch(() => selectedPerson.value, (newPerson) => {
  if (newPerson) {
    updateRadarData(newPerson)
  }
})

// 年份变化时更新统计数据
watch(() => selectedYear.value, () => {
  if (selectedProvince.value) {
    calculateTalentStats(selectedProvince.value.name);
  }
});


// 初始化数据处理
const initPopulationData = () => {
  const uniqueYears = Array.from(new Set(populationData.map(item => item.time))).sort((a, b) => a - b)
  years.value = uniqueYears
  if (uniqueYears.length > 0) {
    selectedYear.value = uniqueYears[0]
  }

  const grouped = {}
  populationData.forEach(item => {
    if (!grouped[item.time]) grouped[item.time] = {}
    grouped[item.time][item.province] = {
      population: item.population,
      frequency: item.frequency
    }
  })
  yearGroupData.value = grouped
}

const initPersonData = () => {
  const grouped = {};
  personTracks.value.forEach(track => {
    if (!grouped[track.time]) {
      grouped[track.time] = {};
    }
    const province = track.province;
    if (!grouped[track.time][province]) {
      grouped[track.time][province] = [];
    }
    grouped[track.time][province].push(track);
  });
  yearProvincePersons.value = grouped;
};

const initTraceData = () => {
  const grouped = {}
  traceData.forEach(item => {
    if (!grouped[item.time]) grouped[item.time] = []
    grouped[item.time].push(item)
  })
  yearTraceData.value = grouped
}

const currentYearData = computed(() => {
  return yearGroupData.value[selectedYear.value] || {}
})

const filterPersonsByYearAndProvince = () => {
  if (!selectedProvince.value || !selectedYear.value) {
    filteredPersons.value = [];
    return;
  }

  const provincePersons = yearProvincePersons.value[selectedYear.value]?.[selectedProvince.value.name] || [];
  const uniquePersons = [];
  const personIds = new Set();
  provincePersons.forEach(person => {
    if (!personIds.has(person.person_id)) {
      personIds.add(person.person_id);
      uniquePersons.push(person);
    }
  });

  filteredPersons.value = uniquePersons;
};

const createYearLabel = (position: number[], years: number[]) => {
  const yearText = years.join('、'); // 将年份数组转为"2023、2025"格式

  return new window.AMap.Text({
    text: yearText,
    position: position, // 省份中心坐标
    offset: new window.AMap.Pixel(0, 20), // 偏移到省份名称下方
    style: {
      backgroundColor: 'rgba(54, 179, 126, 0.9)', // 绿色背景（与轨迹线呼应）
      color: 'white',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      whiteSpace: 'nowrap',
      boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
    },
    zIndex: 21 // 确保在轨迹线之上
  });
};


// 清除人员轨迹和标签
const clearPersonTrace = () => {
  // 清除轨迹线
  personTraceLines.value.forEach(line => {
    if (map.value && line) {
      map.value.remove(line);
    }
  });
  personTraceLines.value = [];

  // 清除轨迹标签
  personTraceLabels.value.forEach(label => {
    if (map.value && label) {
      map.value.remove(label);
    }
  });
  personTraceLabels.value = [];
};

// 新增：绘制人员轨迹线
const drawPersonTrace = (personId) => {
  // 清除已有轨迹和标签
  clearPersonTrace();

  // 收集该人员所有年份的轨迹数据
  const personTraces = personTracks.value.filter(track => track.person_id === personId);

  if (personTraces.length === 0) return;

  // 按省份分组并收集年份
  const provinceYears = {};
  personTraces.forEach(trace => {
    if (!provinceYears[trace.province]) {
      provinceYears[trace.province] = new Set();
    }
    provinceYears[trace.province].add(trace.time);
  });

  // 按年份排序轨迹点
  const sortedTraces = [...personTraces].sort((a, b) => a.time - b.time);

  // 获取轨迹点坐标并创建标签
  const path = [];
  const labels = [];

  for (const province in provinceYears) {
    const provinceData = provinces.value.find(p => p.name === province);
    if (provinceData) {
      // 添加到轨迹路径
      path.push(provinceData.center);

      // 排序年份并创建标签
      const yearArray = Array.from(provinceYears[province]).sort((a, b) => a - b);
      const label = createYearLabel(provinceData.center, yearArray);
      labels.push(label);
    }
  }

  // 绘制轨迹线（至少需要两个点）
  if (path.length >= 2) {
    const traceLine = new window.AMap.Polyline({
      path: path,
      strokeColor: '#36b37e', // 绿色
      strokeWeight: 5, // 粗线
      strokeOpacity: 0.8,
      zIndex: 20, // 确保在其他图层之上
      strokeStyle: 'solid',
      lineJoin: 'round' // 线条连接处圆润
    });

    traceLine.setMap(map.value);
    personTraceLines.value.push(traceLine);
  }

  // 添加标签到地图
  labels.forEach(label => {
    label.setMap(map.value);
    personTraceLabels.value.push(label);
  });
};

// 处理人员选择，添加轨迹绘制
const selectPerson = (person) => {
  const detail = personDetails.value.find(d => d.person_id === person.person_id) || {};
  selectedPerson.value = { ...person, ...detail };
  showPersonDetail.value = true;
  drawPersonTrace(person.person_id); // 绘制该人员的轨迹
};

// 选择省份时清除人员轨迹
const selectProvince = (province) => {
  clearPersonTrace(); // 切换省份时清除轨迹

  selectedProvince.value = province;
  activeProvince.value = province.adcode;
  map.value?.setZoomAndCenter(6, province.center);
  filterPersonsByYearAndProvince();
  updateLabelStyles(province.adcode);
  highlightRelatedLines(province.name);
  showPersonSidebar.value = true;
};

// 切换年份时清除人员轨迹
const handleYearClick = (year) => {
  clearPersonTrace(); // 切换年份时清除轨迹

  selectedYear.value = year;
  updateDistrictColorsByYear(null);
  updateTracesByYear();
};

watch([() => selectedYear.value, () => selectedProvince.value], () => {
  filterPersonsByYearAndProvince()
})

const districtLayer = ref(null)

const highlightRelatedLines = (provinceName) => {
  traceLines.value.forEach(lineInfo => {
    const { polyline, start, end } = lineInfo;
    const isRelated = start === provinceName || end === provinceName;
    polyline.setOptions({
      strokeOpacity: isRelated ? 1 : 0.05,  // 非关联线条降低透明度
      // 保持宽度不变，仅通过透明度区分
      strokeWeight: polyline.getOptions().strokeWeight  // 维持原宽度
    });
  });
};

// 初始化地图
onMounted(() => {
  initPopulationData()
  initTraceData()
  initPersonData()
  initTalentTrendChart()

  window._AMapSecurityConfig = {
    securityJsCode: "8459a6561ceacfac5ce2615f9b602d7e"
  }

  const script = document.createElement('script')
  script.src = 'https://webapi.amap.com/loader.js'
  script.onload = () => {
    window.AMapLoader.load({
      key: "304e8147b61d6b38035924f4cd41237e",
      version: "2.0",
      plugins: ['AMap.Text', 'AMap.DistrictLayer', 'AMap.Polyline']
    }).then((AMap) => {
      // 暴露AMap到window，供后续使用
      window.AMap = AMap;

      map.value = new AMap.Map("m-container", {
        showLabel: false,
        zoom: 4.6,
        center: [105.855339, 36.544393],
        viewMode: '3D',
        mapStyle: 'amap://styles/light',
        pitch: 30,
        rotation: 0
      })

      createProvinceLabels(AMap)
      createDistrictLayer(AMap)
      updateDistrictColorsByYear(AMap)
      createProvinceTraces(AMap)
      updateTracesByYear(AMap)
    })
  }
  document.body.appendChild(script)
})

// 创建省份标签
const createProvinceLabels = (AMap) => {
  provinces.value.forEach(province => {
    const defaultStyle = {
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      color: 'white',
      padding: '4px 8px',
      borderRadius: '3px',
      fontSize: '12px',
      whiteSpace: 'nowrap',
      boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
      transition: 'all 0.1s ease'
    }

    const hoverStyle = {
      ...defaultStyle,
      backgroundColor: 'rgba(64, 158, 255, 0.9)',
      fontSize: '14px',
      boxShadow: '0 3px 8px rgba(0,0,0,0.2)'
    }

    const activeStyle = {
      ...defaultStyle,
      backgroundColor: 'rgba(64, 158, 255, 1)',
      color: 'white',
      fontSize: '14px',
      boxShadow: '0 3px 10px rgba(64, 158, 255, 0.5)'
    }

    const label = new AMap.Text({
      text: province.name,
      position: province.center,
      offset: new AMap.Pixel(-25, -15),
      style: defaultStyle,
      zIndex: 11
    })

    label._provinceData = province

    label.on('mouseover', () => {
      if (activeProvince.value !== province.adcode) {
        label.setStyle(hoverStyle)
      }
    })

    label.on('mouseout', () => {
      if (activeProvince.value !== province.adcode) {
        label.setStyle(defaultStyle)
      }
    })

    label.on('click', () => {
      selectProvince(province)
    })

    label.setMap(map.value)
    textOverlays.value.push({ label, province: province.name })
  })
}

// 更新标签选中状态样式
const updateLabelStyles = (provinceCode) => {
  textOverlays.value.forEach(({ label }) => {
    const province = label._provinceData
    if (province.adcode === provinceCode) {
      label.setStyle({
        backgroundColor: 'rgba(64, 158, 255, 1)',
        color: 'white',
        fontSize: '14px',
        boxShadow: '0 3px 10px rgba(64, 158, 255, 0.5)'
      })
    } else {
      label.setStyle({
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        color: 'white',
        fontSize: '12px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
      })
    }
  })
}

// 创建行政区域图层
const createDistrictLayer = (AMap) => {
  const provinceAdcodes = provinces.value.map(province => province.adcode)

  districtLayer.value = new AMap.DistrictLayer.Province({
    zIndex: 8,
    adcodes: provinceAdcodes,
    depth: 0,
    styles: {
      'fill': (props) => {
        const province = provinces.value.find(
          p => String(p.adcode) === String(props.adcode)
        )?.name

        if (!province) {
          console.log(`未找到匹配省份: ${props.adcode}`)
          return 'rgba(200,200,200,0.3)'
        }

        const data = currentYearData.value
        const provinceData = data[province] || { frequency: 0 }

        const allFrequencies = Object.values(data).map(item => item.frequency)
        const minFreq = Math.min(...allFrequencies, 0)
        const maxFreq = Math.max(...allFrequencies, 0)
        const freqRange = maxFreq - minFreq || 1
        const normalizedFreq = (provinceData.frequency - minFreq) / freqRange

        return getColorByFrequency(normalizedFreq)
      }
    }
  })

  districtLayer.value.setMap(map.value)
}

const getColorByFrequency = (frequency: number) => {
  const normalized = Math.max(0, Math.min(1, frequency))
  const blue = Math.round(255 * (1 - normalized))
  const red = Math.round(255 * normalized)
  return `rgba(${red}, 0, ${blue}, 0.5)`
}

const updateDistrictColorsByYear = (AMap) => {
  if (!districtLayer.value) return

  const latestData = currentYearData.value
  const allFrequencies = Object.values(latestData).map(item => item.frequency)
  const minFreq = allFrequencies.length > 0 ? Math.min(...allFrequencies) : 0
  const maxFreq = allFrequencies.length > 0 ? Math.max(...allFrequencies) : 0
  const freqRange = maxFreq - minFreq || 1

  districtLayer.value.setStyles({
    'fill': (props) => {
      const province = provinces.value.find(
        p => String(p.adcode) === String(props.adcode)
      )?.name

      if (!province) return 'rgba(200,200,200,0.3)'

      const provinceData = latestData[province] || { frequency: 0 }
      const normalizedFreq = (provinceData.frequency - minFreq) / freqRange

      return getColorByFrequency(normalizedFreq)
    }
  })
}

const createProvinceTraces = () => {
  traceLines.value.forEach(lineInfo => map.value?.remove(lineInfo.polyline));
  traceLines.value = [];
};

// 更新轨迹线
const updateTracesByYear = () => {
  traceLines.value.forEach(lineInfo => map.value?.remove(lineInfo.polyline));
  traceLines.value = [];

  const currentTraces = yearTraceData.value[selectedYear.value] || [];
  if (currentTraces.length === 0) return;

  const frequencies = currentTraces.map(trace => trace.frequency);
  const minFreq = Math.min(...frequencies);
  const maxFreq = Math.max(...frequencies);
  const freqRange = maxFreq - minFreq || 1;

  currentTraces.forEach(trace => {
    const startProvince = provinces.value.find(p => p.name === trace.start_province);
    const endProvince = provinces.value.find(p => p.name === trace.end_province);

    if (!startProvince || !endProvince) return;

    // 归一化频率（0~1范围）
    const normalizedFreq = (trace.frequency - minFreq) / freqRange;

    // 1. 计算颜色（蓝→红，已有逻辑）
    const strokeColor = getColorByFrequency(normalizedFreq);

    // 2. 计算线条宽度（细→粗）：基于归一化频率，范围1~5px
    const minWidth = 1;   // 最小宽度
    const maxWidth = 5;   // 最大宽度
    const strokeWidth = minWidth + (maxWidth - minWidth) * normalizedFreq;

    // 创建轨迹线（应用颜色和宽度）
    const polyline = new window.AMap.Polyline({
      path: [
        [startProvince.center[0], startProvince.center[1]],
        [endProvince.center[0], endProvince.center[1]]
      ],
      strokeColor: strokeColor,       // 颜色（蓝→红）
      strokeWeight: strokeWidth,      // 宽度（细→粗）
      strokeOpacity: 0.8,             // 适当提高透明度，增强视觉效果
      zIndex: 10,
      strokeStyle: 'solid',
      lineJoin: 'round'               // 线条连接处圆润，避免尖锐拐角
    });

    traceLines.value.push({
      polyline,
      start: startProvince.name,
      end: endProvince.name
    });

    map.value?.add(polyline);
  });

  if (selectedProvince.value) {
    highlightRelatedLines(selectedProvince.value.name);
  }
};

// 组件卸载时清除轨迹
onUnmounted(() => {
  clearPersonTrace();
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }

  if (trendChartInstance.value) {
    trendChartInstance.value.dispose()
  }
})

watch([() => showPersonDetail.value, () => selectedPerson.value], ([showDetail, person], [oldShow, oldPerson]) => {
  if (showDetail && person) {
    nextTick(() => {
      if (!chartInstance.value) {
        initRadarChart();
      }
      updateRadarData(person);
    });
  }
});
</script>

<style scoped>
/* 原有样式保持不变 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#m-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}

.control-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 250px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.province-list {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 10px;
}

.province-item {
  padding: 8px 10px;
  margin: 3px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.province-item:hover {
  background-color: #f0f0f0;
}

.province-item.active {
  background-color: #409eff;
  color: white;
}

.province-info {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.timeline-container {
  max-width: 50%;
  margin: 0 auto;
  position: absolute;
  bottom: 30px;
  left: 0;
  right: 0;
  z-index: 2;
  padding: 0 20px;
}

.timeline-header {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 12px 20px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
}

.timeline-title {
  display: inline-block;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.timeline-track {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 5px;
  scrollbar-width: thin;
}

.timeline-item {
  padding: 8px 18px;
  background-color: #f1f5f9;
  border-radius: 20px;
  color: #333;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  font-size: 14px;
}

.timeline-item:hover {
  background-color: #e2e8f0;
  transform: translateY(-1px);
}

.timeline-item.active {
  background-color: #409eff;
  color: white;
  font-weight: 500;
}

/* 人员信息侧边栏样式 */
.person-sidebar {
  position: absolute;
  top: 0;
  left: 0;
  width: 320px;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
}

.sidebar-header h3 {
  color: #333;
  margin-bottom: 8px;
  font-size: 16px;
}

.year-indicator {
  color: #666;
  font-size: 13px;
  opacity: 0.8;
}

.person-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  scrollbar-width: thin;
}

/* 人员卡片样式 */
.person-card {
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  /* 显示可点击光标 */
}

.person-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  /* 增强悬停效果 */
}

.person-card:active {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  /* 点击效果 */
}

/* 关闭按钮样式 */
.close-btn {
  background: transparent;
  border: none;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f0f0f0;
  color: #ff4d4f;
}

/* 侧边栏标题栏布局 */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* 详情面板标题栏布局 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.detail-header h3 {
  margin: 0;
  color: #333;
}


.person-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.person-header h4 {
  color: #333;
  font-size: 15px;
}

.industry-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background-color: #e8f4fd;
  color: #409eff;
}

/* 人员信息布局 */
.person-info {
  margin-bottom: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 4px;
}

.info-row p {
  color: #666;
  font-size: 12px;
  flex: 1;
  margin-bottom: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 能力信息布局 */
.abilities {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #f0f0f0;
}

.ability-row {
  display: flex;
  gap: 10px;
  margin-bottom: 4px;
}

.ability-item {
  flex: 1;
  font-size: 12px;
  color: #555;
}

.empty提示 {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
  background-color: white;
  border-radius: 8px;
}

.person-list::-webkit-scrollbar {
  width: 6px;
}

.person-list::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

/* 新增：人员详细信息面板样式 */
.person-detail-panel {
  position: absolute;
  top: 0;
  left: 320px;
  width: 400px;
  /* 加宽面板（原300px → 400px） */
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.15);
  z-index: 2;
  padding: 20px;
  overflow-y: auto;
}

.person-detail-panel h3 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.detail-section {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}


.detail-section h4 {
  color: #409eff;
  margin-bottom: 12px;
  /* 增加标题与内容的间距 */
  font-size: 14px;
  padding-bottom: 5px;
  border-bottom: 1px solid #f0f0f0;
  /* 增加小标题下划线 */
}

.detail-content p {
  color: #555;
  font-size: 13px;
  margin-bottom: 0;
  /* 移除默认底部间距，通过grid-gap控制间距 */
  line-height: 1.5;
  white-space: nowrap;
  /* 防止文字换行 */
  overflow: hidden;
  text-overflow: ellipsis;
  /* 超长文本显示省略号 */
}

.empty-detail {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 14px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}

.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  /* 平均分成两列 */
  gap: 10px 0;
  /* 行间距10px，列间距20px */
}

/* 新增雷达图样式 */
.radar-chart-container {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}

.radar-chart {
  width: 100% !important;
  /* 强制占满父容器宽度 */
  height: 300px !important;
  /* 固定高度，确保可见 */
  min-width: 200px;
  /* 避免容器过窄 */
}


/* 调整能力评估区域布局 */
.detail-section:last-child {
  margin-bottom: 40px;
  /* 增加底部间距，避免图表被截断 */
}


/* 新增：人才统计面板样式 */
.talent-stat-panel {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 2px solid #409eff;
}

.talent-stat-panel h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 16px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.chart-section {
  margin-bottom: 20px;
}

.small-chart {
  width: 100%;
  height: 200px;
  margin-top: 10px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.8);
}

.stat-table {
  margin-bottom: 20px;
}

.stat-table h4 {
  color: #409eff;
  margin-bottom: 10px;
  font-size: 14px;
}

.stat-row {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  margin-bottom: 5px;
  background-color: rgba(245, 247, 250, 0.8);
  border-radius: 4px;
}

.rank {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  margin-right: 10px;
  font-size: 12px;
}

.province-name {
  flex: 1;
  font-size: 13px;
}

.count {
  color: #f56c6c;
  font-weight: 500;
  font-size: 13px;
}

.empty-stat {
  text-align: center;
  padding: 15px;
  color: #999;
  font-size: 13px;
  background-color: rgba(245, 247, 250, 0.5);
  border-radius: 4px;
}

/* 调整控制面板最大高度，允许滚动 */
.control-panel {
  max-height: calc(100vh - 50px);
  overflow-y: auto;
}

/* 省市选择面板定位（右侧上方） */
.province-panel {
  top: 20px;
  right: 20px;
  max-height: 500px;
  /* 限制高度，避免与统计面板重叠 */
}

/* 人才统计面板定位（右侧下方） */
.talent-panel {
  top: 10px;
  /* 位于省市面板下方 */
  right: 20px;
  max-height: 698px;
  /* 适应剩余高度 */
}

/* 统计面板头部（带关闭按钮） */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header h3 {
  margin: 0 auto;
  color: #333;
  font-size: 16px;
}

/* 显示统计面板的按钮 */
.show-talent-btn {
  position: absolute;
  top: 510px;
  /* 位于省市面板下方 */
  right: 20px;
  z-index: 2;
  padding: 8px 15px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: background-color 0.2s;
}

.show-talent-btn:hover {
  background-color: #66b1ff;
}

/* 调整统计面板内部样式 */
.talent-panel .chart-section {
  margin-top: 10px;
}

.talent-panel .stat-table {
  margin-bottom: 15px;
}

/* 确保两个面板样式隔离 */
.control-panel {
  /* 移除原有top和right，由子类定义 */
  position: absolute;
  width: 250px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
  overflow-y: auto;
}
</style>
