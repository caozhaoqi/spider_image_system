# linux command on ubuntu

## use

- For use face detect, you need run follow command on ubuntu:

```shell
sudo apt-get update
sudo apt-get install libgtk2.0-dev pkg-config
# end run follow command
./sh/run_face_detect.sh # (on ubuntu os)
```

## command

- yarn

```shell
// 查询源
yarn config get registry

// 更换国内源
yarn config set registry https://registry.npmmirror.com

// 恢复官方源
yarn config set registry https://registry.yarnpkg.com

// 删除注册表
yarn config delete registry
#最新地址 淘宝 NPM 镜像站喊你切换新域名啦!
npm config set registry https://registry.npmmirror.com

npm install -g cnpm --registry=https://registry.npmmirror.com
 
 # 注册模块镜像
npm set registry https://registry.npmmirror.com  
 
# node-gyp 编译依赖的 node 源码镜像  
npm set disturl https://npmmirror.com/dist 
 
// 清空缓存  
npm cache clean --force  
 
// 安装cnpm  
npm install -g cnpm --registry=https://registry.npmmirror.com  
 
 
 # mirror config
sharp_binary_host = https://npmmirror.com/mirrors/sharp
sharp_libvips_binary_host = https://npmmirror.com/mirrors/sharp-libvips
profiler_binary_host_mirror = https://npmmirror.com/mirrors/node-inspector/
fse_binary_host_mirror = https://npmmirror.com/mirrors/fsevents
node_sqlite3_binary_host_mirror = https://npmmirror.com/mirrors
sqlite3_binary_host_mirror = https://npmmirror.com/mirrors
sqlite3_binary_site = https://npmmirror.com/mirrors/sqlite3
sass_binary_site = https://npmmirror.com/mirrors/node-sass
electron_mirror = https://npmmirror.com/mirrors/electron/
puppeteer_download_host = https://npmmirror.com/mirrors
chromedriver_cdnurl = https://npmmirror.com/mirrors/chromedriver
operadriver_cdnurl = https://npmmirror.com/mirrors/operadriver
phantomjs_cdnurl = https://npmmirror.com/mirrors/phantomjs
python_mirror = https://npmmirror.com/mirrors/python
registry = https://registry.npmmirror.com
disturl = https://npmmirror.com/dist
```

- 关闭防火墙

```shell
systemctl stop firewalld.service
```