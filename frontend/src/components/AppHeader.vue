<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">MyAlbum</router-link>
      <nav class="nav-links">
        <router-link to="/albums">相册</router-link>
        <router-link to="/timeline">时间线</router-link>
        <router-link to="/locations">地点</router-link>
        <router-link to="/admin">管理</router-link>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 16px;
}

.logo {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #1d1d1f;
  text-decoration: none;
  transition: opacity 0.25s;
  font-style: italic;
}
.logo:hover {
  opacity: 0.6;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-links a {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: #424245;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}

.nav-links a:hover {
  color: #1d1d1f;
  background: rgba(0, 0, 0, 0.04);
}

.nav-links a.router-link-exact-active {
  color: #1d1d1f;
  font-weight: 600;
}

@media (max-width: 640px) {
  .logo {
    font-size: 20px;
    letter-spacing: 0.06em;
  }
  .nav-links {
    gap: 0;
  }
  .nav-links a {
    font-size: 13px;
    padding: 6px 8px;
  }
}
</style>
