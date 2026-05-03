<template>
  <el-header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">📷 MyAlbum</router-link>
      <nav class="nav-links">
        <router-link to="/albums">相册</router-link>
        <router-link to="/timeline">时间线</router-link>
        <router-link to="/locations">地点</router-link>
        <router-link to="/admin">管理</router-link>
      </nav>
    </div>
  </el-header>
</template>

<style scoped>
.app-header {
  background: #1e293b;
  border-bottom: 1px solid #334155;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}
.logo {
  color: #e2e8f0;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}
.nav-links {
  display: flex;
  gap: 4px;
}
.nav-links a {
  color: #94a3b8;
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-links a:hover,
.nav-links a.router-link-exact-active {
  color: #e2e8f0;
  background: #334155;
}
@media (max-width: 640px) {
  .logo { font-size: 16px; }
  .nav-links a { padding: 6px 10px; font-size: 12px; }
}
</style>
