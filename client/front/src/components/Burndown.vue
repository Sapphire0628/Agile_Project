<template>
  <v-card v-if="sprintData" class="h-100">
    <v-card-title class="text-subtitle-1">
      Current Sprint Progress
      <v-spacer></v-spacer>
      <span class="text-caption">
        Due Date: {{ formatDateStr(sprintData.due_date) }}
      </span>
    </v-card-title>
    <v-card-text class="flex-grow-1">
      <div ref="burndownChart" class="chart-container"></div>
    </v-card-text>
  </v-card>
  <v-card v-else class="h-100">
    <v-card-text class="text-center">
      No active sprints
    </v-card-text>
  </v-card>
</template>

<script>
import * as echarts from 'echarts'
import { onMounted, onUnmounted, ref, nextTick, watch } from 'vue'
import {getSprints} from '@/api/sprint'

export default {
  name: 'Burndown',
  props: {
    projectId: {
      type: [Number, String],
      required: true,
      validator(value) {
        return value !== undefined && value !== null
      }
    }
  },
  setup(props) {
    const burndownChart = ref(null)
    const sprintData = ref(null)
    let chart = null

    const handleResize = () => {
      if (chart) {
        chart.resize()
      }
    }

    const formatDateStr = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const fetchCurrentSprint = async () => {
      try {
        if (!props.projectId) {
          console.warn('No project ID provided')
          return
        }
        
        console.log('Fetching sprint data for project:', props.projectId)
        const sprintsResponse = await getSprints({project_id: props.projectId})
        const sprints = Object.values(sprintsResponse.data).map(sprint => ({
          due_date: sprint.due_date,
          start_at: sprint.start_at,
          round: sprint.round
        }))
        
        const currentDate = new Date()
        const upcomingSprints = sprints
          .filter(sprint => new Date(sprint.due_date) > currentDate)
          .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))

        if (upcomingSprints.length === 0) {
          sprintData.value = null
          return
        }
        const nearestSprint = upcomingSprints[0]
        const sprintDetailResponse = await getSprints({
          project_id: props.projectId, 
          round: nearestSprint.round  
        })
        sprintData.value = sprintDetailResponse.data
        console.log('sprintData', sprintData.value)

        if (sprintData.value) {
          initChart()
        }
      } catch (error) {
        console.error('Failed to fetch sprint data:', error)
        sprintData.value = null
      }
    }


    const calculateActualBurndown = (tasks, startDate, endDate) => {
      const dates = []
      const actualData = []
 
      const totalPoints = tasks.reduce((sum, task) => sum + (task.priority || 1), 0)
      

      const completedPointsByDate = new Map()
      

      tasks.forEach(task => {
        if (task.done_date && task.done_date !== 'null') {
          const doneDate = new Date(task.done_date)
          const doneDateStr = doneDate.toISOString().split('T')[0]
          
          if (new Date(doneDateStr) >= new Date(startDate)) {
            const priority = task.priority || 1
            const currentPoints = completedPointsByDate.get(doneDateStr) || 0
            completedPointsByDate.set(doneDateStr, currentPoints + priority)
          }
        }
      })

      let remainingPoints = totalPoints 
      let currentDate = new Date(startDate)
      const end = new Date(endDate)
      
      while (currentDate <= end) {
        const currentDateStr = currentDate.toISOString().split('T')[0]
        dates.push(currentDateStr)
        
        const completedPoints = completedPointsByDate.get(currentDateStr) || 0
        if (completedPoints > 0) {
          remainingPoints -= completedPoints
        }
        
        actualData.push(Math.max(0, remainingPoints))
        
        currentDate.setDate(currentDate.getDate() + 1)
      }
      
      return { dates, actualData }
    }

    const calculateIdealBurndown = (tasks, totalDays) => {
      const idealData = []
      const totalPoints = tasks.reduce((sum, task) => sum + (task.priority || 1), 0)
      const pointsPerDay = totalPoints / totalDays
      
      console.log('Ideal burn down line:', {
        totalPoints,
        totalDays,
        pointsPerDay
      })
      
      for (let i = 0; i <= totalDays; i++) {
        const remainingPoints = Math.max(0, totalPoints - (pointsPerDay * i))
        idealData.push(Math.round(remainingPoints * 10) / 10)
      }
      return idealData
    }

    const initChart = async () => {
      await nextTick()
      
      if (!burndownChart.value) {
        console.error('Chart container element does not exist')
        return
      }

      const { start_at, due_date, total_tasks: tasks } = sprintData.value
      
  
      if (!start_at || !due_date || !tasks || tasks.length === 0) {
        console.warn('Missing necessary sprint data')
        return
      }

      const startDate = new Date(start_at)
      const endDate = new Date(due_date)
      const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))


      const idealData = calculateIdealBurndown(tasks, totalDays)
      const { dates, actualData } = calculateActualBurndown(
        tasks,
        start_at,
        due_date
      )


      if (chart) {
        chart.dispose()
      }

      chart = echarts.init(burndownChart.value)
      const option = {
        grid: {
          top: '10%',
          right: '5%',
          bottom: '20%',    
          left: '10%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `Date: ${params[0].axisValue}<br/>
                    ${params[0].seriesName}: ${params[0].data}<br/>
                    ${params[1].seriesName}: ${params[1].data}`
          }
        },
        legend: {
          show: true,
          data: ['Ideal remaining points', 'Actual remaining points'],
          bottom: '10%',    
          left: 'center',   
          itemWidth: 25,   
          itemHeight: 14,   
          textStyle: {
            fontSize: 12    
          },
          itemGap: 30       
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            formatter: (value) => value.slice(5), 
            interval: 'auto',
            rotate: 30,   
            margin: 15     
          },
          boundaryGap: true  
        },
        yAxis: {
          type: 'value',
          name: 'Remaining points',  
          minInterval: 1,
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed',
              opacity: 0.5
            }
          }
        },
        series: [
          {
            name: 'Ideal remaining points', 
            type: 'line',
            data: idealData,
            smooth: true,
            lineStyle: {
              type: 'dashed',
              width: 2
            },
            symbol: 'circle',
            symbolSize: 6,
            showSymbol: false
          },
          {
            name: 'Actual remaining points', 
            type: 'line',
            data: actualData,
            smooth: true,
            lineStyle: {
              width: 2
            },
            symbol: 'circle',
            symbolSize: 6,
            showSymbol: false
          }
        ]
      }
      
      try {
        chart.setOption(option)
        
        const resizeObserver = new ResizeObserver(() => {
          chart && chart.resize()
        })
        resizeObserver.observe(burndownChart.value)
        return () => {
          resizeObserver.disconnect()
        }
      } catch (error) {
        console.error('Chart rendering failed:', error)
      }
    }

    const fetchBurndownData = async () => {
      await fetchCurrentSprint()
    }

    watch(
      () => props.projectId,
      async (newId, oldId) => {
        if (newId !== oldId) {
          console.log('Burndown: projectId changed to', newId)
          await fetchCurrentSprint()
        }
      }
    )

    onMounted(async () => {
      await fetchCurrentSprint()
      
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    
      if (chart) {
        chart.dispose()
        chart = null
      }
    })

    return {
      burndownChart,
      sprintData,
      formatDateStr,
      fetchBurndownData
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
}

:deep(.v-card-text) {
  height: calc(100% - 48px);
  padding-bottom: 8px;
}
</style>
