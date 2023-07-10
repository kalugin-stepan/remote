class Joy {
    clicked = false
    pos = new Int8Array(2)
    constructor(selector) {
        this.parent = document.querySelector(selector)
        this.container = document.createElement('div')
        this.container.style.border = '1px black solid'
        this.container.style.margin = 'auto'
        this.container.style.aspectRatio = '1'
        this.container.style.height = `${this.parent.offsetHeight}px`
        this.parent.appendChild(this.container)
        this.joy = document.createElement('div')
        this.joy.style.borderRadius = '50%'
        this.joy.style.background = 'green'
        this.joy.style.position = 'relative'
        this.joy.style.top = `${this.container.offsetHeight * 0.05}px`
        this.joy.style.left = `${this.container.offsetWidth * 0.05}px`
        this.joy.style.width =  `${this.container.offsetWidth * 0.9}px`
        this.joy.style.height = `${this.container.offsetHeight * 0.9}px`
        this.container.appendChild(this.joy)
        this.events()
    }
    events() {
        this.container.onmousedown = this.on_mouse_down.bind(this)
        this.container.onmousemove = this.on_mouse_move.bind(this)
        this.container.onmouseup = this.on_mouse_up.bind(this)
        this.container.ontouchstart = this.on_touch_down.bind(this)
        this.container.ontouchmove = this.on_touch_move.bind(this)
        this.container.ontouchend = this.on_touch_up.bind(this)
        this.container.ontouchcancel = this.on_touch_up.bind(this)
        window.addEventListener('resize', this.resize.bind(this))
    }
    move(x, y) {
        if (x > this.container.offsetWidth) {
            x = this.container.offsetWidth
        }
        else if (x < 0) {
            x = 0
        }
        if (y > this.container.offsetHeight) {
            y = this.container.offsetHeight
        }
        else if (y < 0) {
            y = 0
        }
        this.joy.style.left = `${x - this.container.offsetWidth * 0.45}px`
        this.joy.style.top = `${y - this.container.offsetHeight * 0.45}px`
        this.pos[0] = Math.round(200 * x / this.container.offsetWidth - 100)
        this.pos[1] = Math.round(-200 * y / this.container.offsetHeight + 100)
    }
    on_mouse_down(e) {
        this.clicked = true
        this.move(e.pageX - this.container.offsetLeft, e.pageY - this.container.offsetTop)
    }
    on_mouse_move(e) {
        if (this.clicked) {
            this.move(e.pageX - this.container.offsetLeft, e.pageY - this.container.offsetTop)
        }
    }
    on_mouse_up(e) {
        this.clicked = false
        this.joy.style.left = `${this.container.offsetWidth * 0.05}px`
        this.joy.style.top = `${this.container.offsetHeight * 0.05}px`
        this.pos[0] = 0
        this.pos[1] = 0
    }
    on_touch_down(e) {
        this.clicked = true
        this.move(e.targetTouches[0].pageX - this.container.offsetLeft, e.targetTouches[0].pageY - this.container.offsetTop)
    }
    on_touch_move(e) {
        if (this.clicked) {
            this.move(e.targetTouches[0].pageX - this.container.offsetLeft, e.targetTouches[0].pageY - this.container.offsetTop)
        }
    }
    on_touch_up(e) {
        this.clicked = false
        this.joy.style.left = `${this.container.offsetWidth * 0.05}px`
        this.joy.style.top = `${this.container.offsetHeight * 0.05}px`
        this.pos[0] = 0
        this.pos[1] = 0
    }
    get_pos() {
        return this.pos
    }
    resize() {
        console.log(this.parent.offsetHeight)
        this.container.style.height = `${this.parent.offsetHeight}px`
        this.joy.style.width = `${this.container.offsetWidth * 0.9}px`
        this.joy.style.height = `${this.container.offsetHeight * 0.9}px`
        this.joy.style.left = `${this.container.offsetWidth * 0.05}px`
        this.joy.style.top = `${this.container.offsetHeight * 0.05}px`
    }
}