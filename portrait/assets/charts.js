(function() {
  'use strict';

  // ========== 模拟数据 ==========
  var customers = [
    { id: 'C-001', name: '张女士', age: 28, gender: '女', city: 'A市', level: 'VIP', score: 92, tags: ['高频消费', '刺身偏好', '午市'], orders: 47, totalSpend: 12860, lastVisit: '今天', avgPrice: 273, frequency: '每周3次', figure: 'young-female.webp' },
    { id: 'C-002', name: '李先生', age: 35, gender: '男', city: 'B市', level: 'SVIP', score: 88, tags: ['商务宴请', '晚市', '高端'], orders: 32, totalSpend: 21500, lastVisit: '昨天', avgPrice: 402, frequency: '每周1次', figure: 'middle-male.webp' },
    { id: 'C-003', name: '王小姐', age: 24, gender: '女', city: 'A市', level: '普通', score: 65, tags: ['新客', '外卖'], orders: 5, totalSpend: 890, lastVisit: '3天前', avgPrice: 178, frequency: '每月1次', figure: 'c003-female.webp' },
    { id: 'C-004', name: '陈先生', age: 42, gender: '男', city: 'C市', level: 'VIP', score: 85, tags: ['家庭聚餐', '周末'], orders: 28, totalSpend: 15400, lastVisit: '2天前', avgPrice: 550, frequency: '每两周1次', figure: 'c004-male.webp' },
    { id: 'C-005', name: '刘女士', age: 31, gender: '女', city: 'A市', level: 'SVIP', score: 95, tags: ['忠实客户', '推荐达人'], orders: 68, totalSpend: 28900, lastVisit: '今天', avgPrice: 425, frequency: '每周4次', figure: 'c005-female.webp' },
    { id: 'C-006', name: '赵先生', age: 29, gender: '男', city: 'B市', level: '普通', score: 72, tags: ['午市', '快餐'], orders: 15, totalSpend: 3200, lastVisit: '5天前', avgPrice: 213, frequency: '每周2次', figure: 'young-male.webp' },
    { id: 'C-007', name: '孙女士', age: 38, gender: '女', city: 'C市', level: 'VIP', score: 78, tags: ['健康轻食', '沙拉'], orders: 22, totalSpend: 7800, lastVisit: '1天前', avgPrice: 355, frequency: '每周2次', figure: 'middle-female.webp' },
    { id: 'C-008', name: '周先生', age: 45, gender: '男', city: 'A市', level: 'SVIP', score: 91, tags: ['商务', '高端', '收藏'], orders: 41, totalSpend: 19800, lastVisit: '今天', avgPrice: 483, frequency: '每周2次', figure: 'c008-male.webp' },
    { id: 'C-009', name: '吴小姐', age: 26, gender: '女', city: 'B市', level: '普通', score: 58, tags: ['尝鲜', '一次客'], orders: 2, totalSpend: 320, lastVisit: '2周前', avgPrice: 160, frequency: '仅1次', figure: 'c009-female.webp' },
    { id: 'C-010', name: '郑先生', age: 33, gender: '男', city: 'C市', level: 'VIP', score: 82, tags: ['家庭', '儿童餐'], orders: 19, totalSpend: 8900, lastVisit: '4天前', avgPrice: 468, frequency: '每月2次', figure: 'c010-male.webp' }
  ];

  var currentCustomer = customers[0];
  var charts = {};

  // ========== 时钟 ==========
  function updateClock() {
    var now = new Date();
    var h = String(now.getHours()).padStart(2, '0');
    var m = String(now.getMinutes()).padStart(2, '0');
    var s = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('clock').textContent = h + ':' + m + ':' + s;
  }
  setInterval(updateClock, 1000);
  updateClock();

  // ========== 渲染客群列表 ==========
  function renderCustomerList(filter) {
    var list = document.getElementById('customerList');
    var filtered = customers.filter(function(c) {
      return !filter || c.id.toLowerCase().includes(filter.toLowerCase()) || c.name.includes(filter);
    });

    list.innerHTML = filtered.map(function(c) {
      var activeClass = c.id === currentCustomer.id ? ' active' : '';
      var levelColor = c.level === 'SVIP' ? '#ffd93d' : c.level === 'VIP' ? '#00f0ff' : '#6a8db5';
      return '<div class="customer-item' + activeClass + '" data-id="' + c.id + '">' +
        '<div class="customer-avatar" style="color:' + levelColor + '">' + c.name[0] + '</div>' +
        '<div class="customer-info">' +
          '<div class="customer-id">' + c.id + ' · ' + c.name + '</div>' +
          '<div class="customer-meta">' + c.age + '岁 / ' + c.gender + ' / ' + c.city + '</div>' +
        '</div>' +
        '<div class="customer-score">' + c.score + '</div>' +
      '</div>';
    }).join('');

    // 绑定点击事件
    list.querySelectorAll('.customer-item').forEach(function(item) {
      item.addEventListener('click', function() {
        var id = this.getAttribute('data-id');
        currentCustomer = customers.find(function(c) { return c.id === id; });
        renderCustomerList(document.getElementById('searchInput').value);
        renderMainContent();
      });
    });
  }

  // ========== 渲染主内容 ==========
  function renderMainContent() {
    var c = currentCustomer;
    var levelColor = c.level === 'SVIP' ? '#ffd93d' : c.level === 'VIP' ? '#00f0ff' : '#6a8db5';

    var tagsHtml = c.tags.map(function(t) {
      var cls = '';
      if (t === '高频消费' || t === '忠实客户') cls = 'gold';
      if (t === '商务宴请' || t === '高端') cls = 'warning';
      return '<span class="tag ' + cls + '">' + t + '</span>';
    }).join('');

    // 每位客户使用专属人物图片
    var figureFile = c.figure;
    var figureDesc = c.tags.slice(0, 3).join('/') + ' · ' + c.city + ' · ' + c.level + '会员';

    var mainHtml =
      // 左栏：身份信息 + 关键指标 + 消费偏好
      '<div class="stage-left">' +
        '<div class="profile-header">' +
          '<div class="profile-basic">' +
            '<div class="profile-avatar-lg" style="background:linear-gradient(135deg,' + levelColor + ',' + levelColor + '88)">' + c.name[0] + '</div>' +
            '<div>' +
              '<div class="profile-name">' + c.name + '</div>' +
              '<div style="font-size:13px;color:var(--muted);margin-top:4px">' + c.age + '岁 · ' + c.gender + ' · ' + c.city + ' · ' + c.level + '会员</div>' +
              '<div class="profile-tags">' + tagsHtml + '</div>' +
            '</div>' +
          '</div>' +
          '<div class="profile-actions">' +
            '<button class="btn btn-outline">导出画像</button>' +
            '<button class="btn btn-primary">发送优惠券</button>' +
          '</div>' +
        '</div>' +
        '<div class="stats-grid">' +
          '<div class="stat-card"><div class="label">📊 累计订单</div><div class="value">' + c.orders + '</div><div class="trend up">↑ 12% 较上月</div></div>' +
          '<div class="stat-card"><div class="label">💰 累计消费</div><div class="value">¥' + (c.totalSpend / 10000).toFixed(1) + 'w</div><div class="trend up">↑ 8% 较上月</div></div>' +
          '<div class="stat-card"><div class="label">🍣 客单价</div><div class="value">¥' + c.avgPrice + '</div><div class="trend up">↑ 5% 较上月</div></div>' +
          '<div class="stat-card"><div class="label">📅 最近到店</div><div class="value">' + c.lastVisit + '</div><div class="trend" style="color:var(--muted)">' + c.frequency + '</div></div>' +
        '</div>' +
        '<div class="panel">' +
          '<div class="panel-header"><div class="panel-title">消费偏好雷达</div><div class="panel-extra">近90天</div></div>' +
          '<div id="chartRadar" class="chart-container"></div>' +
        '</div>' +
      '</div>' +

      // 中栏：全息人物（页面正中央）
      '<aside class="figure-wrap">' +
        '<div class="figure-label">全息投影 · 3D MODEL｜拖动可旋转</div>' +
        '<div class="figure-badge">HOLOGRAM</div>' +
        '<div class="figure-img-box">' +
          '<div class="figure-tilt">' +
            '<img class="figure-img" src="assets/' + figureFile + '" alt="' + c.name + '">' +
          '</div>' +
          '<div class="figure-platform"></div>' +
        '</div>' +
        '<div class="figure-halo"></div>' +
        '<div class="figure-particles" id="figureParticles"></div>' +
        '<div class="figure-info">' +
          '<div class="figure-name">' + c.name + '</div>' +
          '<div class="figure-desc">' + figureDesc + '</div>' +
          '<div class="figure-id">ID: ' + c.id + '</div>' +
        '</div>' +
      '</aside>' +

      // 右栏：时段分布 + 购买记录 + 标签
      '<div class="stage-right">' +
        '<div class="panel">' +
          '<div class="panel-header"><div class="panel-title">消费时段分布</div><div class="panel-extra">近30天</div></div>' +
          '<div id="chartTime" class="time-chart"></div>' +
        '</div>' +
        '<div class="panel">' +
          '<div class="panel-header"><div class="panel-title">最近购买记录</div><div class="panel-extra">共 ' + c.orders + ' 单</div></div>' +
          '<div class="order-list" id="orderList"></div>' +
        '</div>' +
        '<div class="panel">' +
          '<div class="panel-header"><div class="panel-title">客户标签</div><div class="panel-extra">AI 生成</div></div>' +
          '<div class="tag-cloud">' + generateTagCloud(c) + '</div>' +
          '<div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--rule)">' +
            '<div style="font-size:13px;color:var(--muted);margin-bottom:8px">复购概率预测</div>' +
            '<div style="display:flex;align-items:center;gap:12px">' +
              '<div style="flex:1;height:8px;background:var(--bg3);border-radius:4px;overflow:hidden">' +
                '<div style="width:' + c.score + '%;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:4px"></div>' +
              '</div>' +
              '<span style="font-size:18px;font-weight:700;color:var(--accent)">' + c.score + '%</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';

    document.getElementById('mainContent').innerHTML = mainHtml;

    // 渲染订单列表
    renderOrders(c);

    // 初始化图表
    initCharts(c);

    // 生成全息粒子
    initFigureParticles();
    initFigureDrag();
  }

  // ========== 生成标签云 ==========
  function generateTagCloud(c) {
    var allTags = ['三文鱼刺身', '北极贝', '甜虾', '寿司拼盘', '味增汤', '可生食', '冷链直达', '午市套餐', '会员日', '新品试吃', '儿童套餐', '低卡轻食', '高端食材', '节日礼盒', '外卖达人'];
    var selected = allTags.slice(0, 8 + Math.floor(Math.random() * 4));
    return selected.map(function(t, i) {
      return '<span class="cloud-tag' + (i < 3 ? ' active' : '') + '">' + t + '</span>';
    }).join('');
  }

  // ========== 渲染订单 ==========
  function renderOrders(c) {
    var items = [
      { name: '挪威三文鱼刺身拼盘', qty: 1, price: 298, status: 'completed', time: '今天 12:30' },
      { name: '北极贝刺身', qty: 2, price: 128, status: 'completed', time: '昨天 19:15' },
      { name: '三文鱼寿司卷', qty: 3, price: 88, status: 'completed', time: '3天前 18:45' },
      { name: '甜虾刺身', qty: 1, price: 158, status: 'pending', time: '5天前 12:00' },
      { name: '海鲜沙拉', qty: 1, price: 68, status: 'completed', time: '1周前 13:20' }
    ];

    var statusMap = { completed: '已完成', pending: '待配送', refund: '已退款' };
    var statusClass = { completed: 'completed', pending: 'pending', refund: 'refund' };

    document.getElementById('orderList').innerHTML = items.map(function(item) {
      return '<div class="order-item">' +
        '<div class="order-img">🍣</div>' +
        '<div class="order-info">' +
          '<div class="order-name">' + item.name + '</div>' +
          '<div class="order-meta">' + item.time + ' · x' + item.qty + '</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div class="order-price">¥' + item.price + '</div>' +
          '<span class="order-status ' + statusClass[item.status] + '">' + statusMap[item.status] + '</span>' +
        '</div>' +
      '</div>';
    }).join('');
  }

  // ========== 初始化图表 ==========
  function initCharts(c) {
    // 销毁旧图表
    if (charts.radar) charts.radar.dispose();
    if (charts.time) charts.time.dispose();

    // 雷达图 - 消费偏好
    var radarEl = document.getElementById('chartRadar');
    if (radarEl) {
      charts.radar = echarts.init(radarEl, null, { renderer: 'svg' });
      var score = c.score;
      charts.radar.setOption({
        animation: false,
        radar: {
          indicator: [
            { name: '刺身类', max: 100 },
            { name: '寿司类', max: 100 },
            { name: '熟食类', max: 100 },
            { name: '饮品类', max: 100 },
            { name: '甜点类', max: 100 },
            { name: '套餐类', max: 100 }
          ],
          shape: 'polygon',
          splitNumber: 4,
          axisName: { color: '#6a8db5', fontSize: 11 },
          splitLine: { lineStyle: { color: 'rgba(0,240,255,0.1)' } },
          splitArea: { show: true, areaStyle: { color: ['rgba(0,240,255,0.02)', 'rgba(0,240,255,0.05)'] } },
          axisLine: { lineStyle: { color: 'rgba(0,240,255,0.15)' } }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [85 + Math.random() * 10, 60 + Math.random() * 20, 40 + Math.random() * 20, 30 + Math.random() * 20, 50 + Math.random() * 20, 70 + Math.random() * 20],
            name: '消费偏好',
            areaStyle: { color: 'rgba(0, 240, 255, 0.2)' },
            lineStyle: { color: '#00f0ff', width: 2 },
            itemStyle: { color: '#00f0ff' },
            symbolSize: 5
          }]
        }]
      });
    }

    // 时段分布
    var timeEl = document.getElementById('chartTime');
    if (timeEl) {
      charts.time = echarts.init(timeEl, null, { renderer: 'svg' });
      charts.time.setOption({
        animation: false,
        grid: { left: 40, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: ['10-12', '12-14', '14-16', '16-18', '18-20', '20-22'],
          axisLabel: { color: '#6a8db5', fontSize: 10 },
          axisLine: { lineStyle: { color: 'rgba(0,240,255,0.15)' } }
        },
        yAxis: {
          type: 'value',
          axisLabel: { color: '#6a8db5', fontSize: 10 },
          splitLine: { lineStyle: { color: 'rgba(0,240,255,0.08)' } }
        },
        series: [{
          type: 'bar',
          data: [12, 45, 8, 15, 38, 22],
          barWidth: 20,
          itemStyle: {
            color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [{ offset: 0, color: '#00f0ff' }, { offset: 1, color: '#00a8cc' }]
            },
            borderRadius: [4, 4, 0, 0]
          }
        }]
      });
    }
  }

  // ========== 全息粒子 ==========
  function initFigureParticles() {
    var box = document.getElementById('figureParticles');
    if (!box) return;
    var html = '';
    for (var i = 0; i < 18; i++) {
      var left = 15 + Math.random() * 70;
      var delay = Math.random() * 3.5;
      var dur = 2.5 + Math.random() * 2;
      var size = 1.5 + Math.random() * 2.5;
      html += '<span style="left:' + left + '%;bottom:' + (10 + Math.random() * 15) + '%;width:' + size + 'px;height:' + size + 'px;animation-delay:' + delay + 's;animation-duration:' + dur + 's"></span>';
    }
    box.innerHTML = html;
  }

  // ========== 鼠标拖动旋转人物 ==========
  function initFigureDrag() {
    var box = document.querySelector('.figure-img-box');
    var img = document.querySelector('.figure-img');
    if (!box || !img) return;

    var dragging = false;
    var startX = 0, startY = 0, baseRotY = 0, baseRotX = 0, rotY = 0, rotX = 0;

    function clamp(v, min, max) { return v < min ? min : (v > max ? max : v); }

    function apply() {
      img.style.transform = 'rotateY(' + rotY.toFixed(2) + 'deg) rotateX(' + rotX.toFixed(2) + 'deg)';
    }

    // 松手后若停在大角度，缓慢回正到最近的复位位置
    function settle() {
      if (Math.abs(rotY) > 30 || Math.abs(rotX) > 12) {
        rotY = clamp(rotY, -30, 30);
        rotX = clamp(rotX, -12, 12);
        apply();
      }
    }

    box.addEventListener('pointerdown', function (e) {
      dragging = true;
      startX = e.clientX;
      startY = e.clientY;
      baseRotY = rotY;
      baseRotX = rotX;
      box.classList.add('is-dragging');
      if (box.setPointerCapture) {
        try { box.setPointerCapture(e.pointerId); } catch (err) {}
      }
      e.preventDefault();
    });

    box.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      rotY = clamp(baseRotY + (e.clientX - startX) * 0.5, -45, 45);
      rotX = clamp(baseRotX - (e.clientY - startY) * 0.18, -16, 16);
      apply();
    });

    function stop() {
      if (!dragging) return;
      dragging = false;
      box.classList.remove('is-dragging');
      settle();
    }
    box.addEventListener('pointerup', stop);
    box.addEventListener('pointercancel', stop);

    // 双击复位
    box.addEventListener('dblclick', function () {
      rotY = 0;
      rotX = 0;
      apply();
    });
  }

  // ========== 搜索 ==========
  document.getElementById('searchInput').addEventListener('input', function() {
    renderCustomerList(this.value);
  });

  // ========== 初始化 ==========
  renderCustomerList();
  renderMainContent();

  // 窗口resize
  window.addEventListener('resize', function() {
    if (charts.radar) charts.radar.resize();
    if (charts.time) charts.time.resize();
  });
})();
