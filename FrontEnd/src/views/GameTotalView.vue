<template>
  <div class="light-container" @click="closeDropdowns">
    
    <!-- 필터 헤더 -->
    <div class="filter-header" :class="{ 'scrolled': isScrolled }">
      <div class="logo-area">
        <h2 class="brand-logo">Game Library</h2>
      </div>
      
      <div class="filter-group" @click.stop>
        
        <!-- 1. 장르 필터 -->
        <div class="custom-dropdown">
          <button class="dropdown-btn" @click="toggleDropdown('genre')" :class="{ active: showGenre }">
            {{ genreLabel }}
            <span class="icon">▼</span>
          </button>
          
          <div v-if="showGenre" class="dropdown-panel genre-panel">
            <div class="panel-header">장르 선택</div>
            <div class="genre-grid">
              <label 
                v-for="g in genreList" 
                :key="g" 
                class="genre-chip"
                :class="{ selected: selectedGenres.includes(g) }"
              >
                <input type="checkbox" :value="g" v-model="selectedGenres" hidden>
                {{ g }}
              </label>
            </div>
            <div class="panel-footer">
              <button class="btn-reset" @click="selectedGenres = []">초기화</button>
              <button class="btn-apply" @click="applyFilter">적용하기</button>
            </div>
          </div>
        </div>

        <!-- 2. 가격 필터 -->
        <div class="custom-dropdown">
          <button class="dropdown-btn" @click="toggleDropdown('price')" :class="{ active: showPrice }">
            {{ priceLabel }}
            <span class="icon">▼</span>
          </button>
          
          <div v-if="showPrice" class="dropdown-panel price-panel">
            <div class="panel-header">가격 범위 설정</div>
            <div class="price-inputs">
              <div class="input-wrap">
                <span class="currency">₩</span>
                <input type="number" v-model.number="tempMinPrice" @input="validateInput" placeholder="최소" min="0" :max="sliderMax">
              </div>
              <span class="dash">~</span>
              <div class="input-wrap">
                <span class="currency">₩</span>
                <input type="number" v-model.number="tempMaxPrice" @input="validateInput" placeholder="최대" min="0" :max="sliderMax">
              </div>
            </div>

            <div class="slider-container">
              <div class="slider-track-bg"></div>
              <div class="slider-track-fill" :style="{ left: minPercent + '%', width: (maxPercent - minPercent) + '%' }"></div>
              <input type="range" min="0" :max="sliderMax" step="1000" v-model.number="tempMinPrice" @input="validateRange" class="range-input min-range">
              <input type="range" min="0" :max="sliderMax" step="1000" v-model.number="tempMaxPrice" @input="validateRange" class="range-input max-range">
            </div>
            
            <div class="range-labels">
              <span>0원</span>
              <span>{{ sliderMax.toLocaleString() }}+</span>
            </div>

            <div class="panel-footer">
              <button class="btn-reset" @click="resetPrice">초기화</button>
              <button class="btn-apply" @click="applyFilter">적용하기</button>
            </div>
          </div>
        </div>

        <!-- 3. 정렬 필터 -->
        <div class="custom-dropdown">
          <button class="dropdown-btn" @click="toggleDropdown('sort')" :class="{ active: showSort }">
            {{ sortLabel }}
            <span class="icon">▼</span>
          </button>
          <div v-if="showSort" class="dropdown-panel sort-panel">
            <div 
              class="sort-item" 
              v-for="opt in sortOptions" 
              :key="opt.val"
              @click="selectSort(opt.val)"
              :class="{ active: currentSort === opt.val }"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 게임 리스트 영역 -->
    <div class="content-wrapper">
      <div class="game-list">
        <div 
          v-for="game in games" 
          :key="game.appid" 
          class="game-item"
          @click="goDetail(game.appid)"
        >
          <!-- 왼쪽: 썸네일 -->
          <div class="item-thumbnail">
            <img :src="game.header_image" loading="lazy" alt="game cover" />
            <span v-if="game.price === 0" class="badge-free">FREE</span>
          </div>

          <!-- 오른쪽: 정보 -->
          <div class="item-info">
            <div class="info-main">
              <h3 class="game-title">{{ game.title }}</h3>
              <span class="genre">{{ getMainGenre(game.genres) }}</span>
            </div>
            
            <div class="info-side">
              <span class="release-date">{{ formatDate(game.release_date) }}</span>
              <span class="price" :class="{'is-free': game.price === 0}">
                {{ formatPrice(game.price) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 로딩 및 결과 없음 -->
      <div ref="observerTarget" class="loading-trigger">
        <div v-if="loading" class="spinner"></div>
      </div>
      
      <div v-if="!loading && games.length === 0" class="empty-msg">
        조건에 맞는 게임이 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_URL = 'http://127.0.0.1:8000/games/list/' 

// 데이터 상태
const games = ref([])
const loading = ref(false)
const hasMore = ref(true)
const totalCount = ref(0)
const isScrolled = ref(false)

// 드롭다운 UI 상태
const showGenre = ref(false)
const showPrice = ref(false)
const showSort = ref(false)

// 필터 값 상태
const selectedGenres = ref([])
const currentSort = ref('recent')
const finalMinPrice = ref(null) 
const finalMaxPrice = ref(null)

// 가격 설정 (요청하신대로 0 ~ 50,000)
const sliderMax = 50000 
const minGap = 2500

const tempMinPrice = ref(0)
const tempMaxPrice = ref(sliderMax)

const limit = 20 // 리스트 뷰니까 한 번에 불러오는 개수를 살짝 줄임 (선택사항)
const offset = ref(0)

const genreList = ['액션', '어드벤처', 'RPG', '전략', '시뮬레이션', '스포츠', '레이싱', '인디', '캐주얼', '공포', '대규모 멀티플레이어']

const sortOptions = [
  { val: 'recent', label: '최신순' },
  { val: 'price_asc', label: '낮은 가격순' },
  { val: 'price_desc', label: '높은 가격순' },
  { val: 'name', label: '이름순' }
]

// Computed
const genreLabel = computed(() => {
  if (selectedGenres.value.length === 0) return '모든 장르'
  if (selectedGenres.value.length === 1) return selectedGenres.value[0]
  return `${selectedGenres.value[0]} 외 ${selectedGenres.value.length - 1}개`
})

const priceLabel = computed(() => {
  if (finalMinPrice.value === null && finalMaxPrice.value === null) return '모든 가격'
  const minText = finalMinPrice.value ? finalMinPrice.value.toLocaleString() : '0'
  const maxText = (finalMaxPrice.value === null) ? '제한 없음' : finalMaxPrice.value.toLocaleString()
  if (finalMaxPrice.value === 0) return '무료 게임'
  return `${minText} ~ ${maxText}`
})

const sortLabel = computed(() => sortOptions.find(o => o.val === currentSort.value)?.label || '정렬')

const minPercent = computed(() => (tempMinPrice.value / sliderMax) * 100)
const maxPercent = computed(() => (tempMaxPrice.value / sliderMax) * 100)

// Methods
const toggleDropdown = (type) => {
  if (type !== 'genre') showGenre.value = false
  if (type !== 'price') showPrice.value = false
  if (type !== 'sort') showSort.value = false

  if (type === 'genre') showGenre.value = !showGenre.value
  if (type === 'price') {
    tempMinPrice.value = finalMinPrice.value !== null ? finalMinPrice.value : 0
    tempMaxPrice.value = finalMaxPrice.value !== null ? finalMaxPrice.value : sliderMax
    showPrice.value = !showPrice.value
  }
  if (type === 'sort') showSort.value = !showSort.value
}

const closeDropdowns = () => { showGenre.value = false; showPrice.value = false; showSort.value = false; }

const validateRange = (e) => {
  let min = parseInt(tempMinPrice.value)
  let max = parseInt(tempMaxPrice.value)
  if (max - min < minGap) {
    if (e.target.classList.contains('min-range')) tempMinPrice.value = max - minGap
    else tempMaxPrice.value = min + minGap
  }
}

const validateInput = () => {
  if (tempMinPrice.value < 0) tempMinPrice.value = 0
  if (tempMaxPrice.value > sliderMax) tempMaxPrice.value = sliderMax
}

const resetPrice = () => { tempMinPrice.value = 0; tempMaxPrice.value = sliderMax }

const selectSort = (val) => { currentSort.value = val; showSort.value = false; applyFilter(); }

const applyFilter = () => {
  finalMinPrice.value = tempMinPrice.value
  if (tempMaxPrice.value >= sliderMax) finalMaxPrice.value = null 
  else finalMaxPrice.value = tempMaxPrice.value

  closeDropdowns()
  offset.value = 0
  fetchGames(true)
}

const fetchGames = async (isReset) => {
  if (loading.value) return
  loading.value = true
  try {
    const params = {
      limit, offset: offset.value,
      genre: selectedGenres.value.join(','),
      min_price: finalMinPrice.value, max_price: finalMaxPrice.value,
      sort: currentSort.value
    }
    const res = await axios.get(API_URL, { params })
    if (isReset) games.value = res.data.results
    else games.value = [...games.value, ...res.data.results]
    totalCount.value = res.data.count
    hasMore.value = games.value.length < totalCount.value
  } catch (e) { console.error(e) } 
  finally { loading.value = false }
}

const loadMore = () => { offset.value += limit; fetchGames(false); }

// Lifecycle
const observerTarget = ref(null)
let observer = null
onMounted(() => {
  fetchGames(true)
  window.addEventListener('scroll', () => { isScrolled.value = window.scrollY > 20 })
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore.value && !loading.value) loadMore()
  }, { threshold: 0.1 })
  if (observerTarget.value) observer.observe(observerTarget.value)
})
onUnmounted(() => { if (observer) observer.disconnect() })

// Utils
const goDetail = (id) => router.push({ name: 'GameDetail', params: { id } })
const formatPrice = (p) => p === 0 ? 'Free' : `₩${p.toLocaleString()}`
const getMainGenre = (g) => g ? g.split(',')[0] : 'Etc'
const formatDate = (d) => d || ''
</script>

<style scoped>
.light-container { background-color: #f8f9fa; min-height: 100vh; color: #333; }
.content-wrapper { padding: 30px 40px; max-width: 1200px; margin: 0 auto; }

/* 리스트 스타일로 변경 (Grid -> Flex Column) */
.game-list {
  display: flex;
  flex-direction: column;
  gap: 15px; /* 아이템 간 간격 */
}

/* 리스트 아이템 (가로형 카드) */
.game-item {
  display: flex; /* 가로 배치 */
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  height: 110px; /* 높이 고정 (compact) */
  border: 1px solid #f0f0f0;
}

.game-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  border-color: #e0e0e0;
}

/* 썸네일 영역 (작게, 비율 유지) */
.item-thumbnail {
  width: 196px; /* 16:9 비율에 맞춤 (110px 높이 기준) */
  height: 100%;
  position: relative;
  flex-shrink: 0; /* 줄어들지 않음 */
  background-color: #eee;
}

.item-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge-free {
  position: absolute; top: 6px; left: 6px;
  background: rgba(0, 122, 255, 0.9); color: white;
  padding: 3px 6px; border-radius: 4px;
  font-size: 0.7rem; font-weight: 700;
}

/* 정보 영역 (우측으로 이동) */
.item-info {
  flex-grow: 1;
  display: flex;
  justify-content: space-between; /* 제목(좌) - 가격(우) 분리 */
  align-items: center;
  padding: 0 25px;
}

/* 제목 및 장르 */
.info-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  max-width: 60%; /* 너무 길면 말줄임 */
}

.game-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1d1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.genre {
  font-size: 0.85rem;
  color: #86868b;
  background: #f5f5f7;
  padding: 2px 8px;
  border-radius: 4px;
  align-self: flex-start; /* 왼쪽 정렬 */
}

/* 가격 및 날짜 */
.info-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 100px;
}

.price {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d1d1f;
}
.price.is-free { color: #007aff; }

.release-date {
  font-size: 0.8rem;
  color: #aaa;
}


/* --- (아래는 기존 필터/헤더 스타일 동일) --- */
.filter-header {
  position: sticky; top: 0; z-index: 100;
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 40px;
  background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;
}
.filter-header.scrolled { padding: 10px 40px; background: rgba(255, 255, 255, 0.98); box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.brand-logo { margin: 0; font-size: 1.5rem; font-weight: 800; color: #111; }
.filter-group { display: flex; gap: 12px; }
.custom-dropdown { position: relative; }
.dropdown-btn {
  background: #fff; border: 1px solid #e1e4e8;
  padding: 8px 16px; border-radius: 20px;
  font-size: 0.9rem; font-weight: 600; color: #444;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
  transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.dropdown-btn:hover { background-color: #fafafa; border-color: #ccc; }
.dropdown-btn.active { border-color: #007aff; color: #007aff; background-color: #eff6ff; }
.icon { font-size: 0.7rem; color: #888; }
.dropdown-panel {
  position: absolute; top: 120%; right: 0;
  background: #fff; border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15); border: 1px solid #eee;
  padding: 20px; z-index: 200;
  min-width: 280px; animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { font-size: 1rem; font-weight: 700; margin-bottom: 15px; color: #111; }
.panel-footer { display: flex; justify-content: space-between; margin-top: 20px; pt: 15px; border-top: 1px solid #eee; }
.btn-reset { background: none; border: none; color: #888; cursor: pointer; font-size: 0.9rem; }
.btn-apply { background: #007aff; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.genre-panel { width: 320px; }
.genre-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.genre-chip { padding: 6px 12px; border-radius: 20px; background: #f0f2f5; color: #555; font-size: 0.85rem; cursor: pointer; transition: 0.2s; user-select: none; }
.genre-chip.selected { background: #007aff; color: #fff; font-weight: 600; }
.price-panel { width: 320px; }
.price-inputs { display: flex; align-items: center; gap: 10px; margin-bottom: 25px; }
.input-wrap { display: flex; align-items: center; background: #f5f5f7; padding: 8px 12px; border-radius: 8px; flex: 1; }
.input-wrap input { width: 100%; border: none; background: transparent; outline: none; font-size: 0.9rem; font-weight: 600; }
.currency { font-size: 0.9rem; color: #888; margin-right: 5px; }
.dash { color: #ccc; }
.slider-container { position: relative; width: 100%; height: 6px; margin-top: 10px; margin-bottom: 20px; }
.slider-track-bg { position: absolute; top: 0; left: 0; right: 0; height: 100%; background: #eee; border-radius: 3px; z-index: 1; }
.slider-track-fill { position: absolute; top: 0; height: 100%; background: #007aff; border-radius: 3px; z-index: 2; }
.range-input { position: absolute; top: 50%; left: 0; width: 100%; transform: translateY(-50%); background: none; pointer-events: none; appearance: none; z-index: 3; margin: 0; }
.range-input::-webkit-slider-thumb { pointer-events: auto; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #fff; border: 2px solid #007aff; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.range-input::-moz-range-thumb { pointer-events: auto; width: 20px; height: 20px; border-radius: 50%; background: #fff; border: 2px solid #007aff; cursor: pointer; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.range-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-top: -10px; }
.sort-panel { padding: 10px; min-width: 160px; }
.sort-item { padding: 10px 15px; border-radius: 8px; cursor: pointer; font-size: 0.95rem; color: #444; }
.sort-item:hover { background: #f5f5f7; }
.sort-item.active { color: #007aff; font-weight: 700; background: #eff6ff; }
.loading-trigger { height: 80px; display: flex; justify-content: center; align-items: center; }
.spinner { width: 30px; height: 30px; border: 3px solid rgba(0,0,0,0.1); border-top-color: #333; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-msg { text-align: center; padding: 60px; font-size: 1.2rem; color: #888; }

/* 모바일 대응 */
@media (max-width: 768px) {
  .game-item { flex-direction: column; height: auto; }
  .item-thumbnail { width: 100%; height: 200px; }
  .item-info { padding: 15px; flex-direction: row; align-items: center; }
  .info-side { align-items: flex-end; }
}
</style>