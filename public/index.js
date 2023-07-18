// const client = mqtt.connect('ws://192.168.177.67:9001/mqtt')
const client = mqtt.connect('ws://10.23.202.66:9001/mqtt')
// const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt')

const play = new Audio('/public/sound/play.mp3')

let robot_id = localStorage.getItem('robot_id')

const robot_id_input = document.getElementById('robot_id')

if (robot_id !== null) robot_id_input.value = robot_id

robot_id_input.onchange = e => {
    robot_id = robot_id_input.value
    localStorage.setItem('robot_id', robot_id)
    play.play()
}

const joy = new Joy('#joy')

const dir = {
    F: false,
    B: false,
    R: false,
    L: false
}

const key_dir = {
    w: 'F',
    s: 'B',
    a: 'L',
    d: 'R'
}

const on_press = btn => dir[btn] = true

const on_release = btn => dir[btn] = false

onkeydown = e => {
    const key = e.key.toLowerCase()
    if (!Object.keys(key_dir).includes(key)) return
    on_press(key_dir[key])
}

onkeyup = e => {
    const key = e.key.toLowerCase()
    if (!Object.keys(key_dir).includes(key)) return
    on_release(key_dir[key])
}

let last_x = 0
let last_y = 0

let last_btn_x = 0
let last_btn_y = 0

const btn_pos = new Int8Array(2)

setInterval(() => {
    const pos = joy.get_pos()
    if (pos[0] !== last_x || pos[1] !== last_y) {
        last_x = pos[0]
        last_y = pos[1] 
        client.publish(robot_id, new Uint8Array(pos.buffer))
        return
    }
    btn_pos[0] = 0
    btn_pos[1] = 0
    if (dir.F) {
        btn_pos[1] += 100
    }
    if (dir.B) {
        btn_pos[1] -= 100
    }
    if (dir.L) {
        btn_pos[0] -= 100
    }
    if (dir.R) {
        btn_pos[0] += 100
    }
    if (btn_pos[0] !== last_btn_x || btn_pos[1] !== last_btn_y) {
        client.publish(robot_id, new Uint8Array(btn_pos.buffer))
        last_btn_x = btn_pos[0]
        last_btn_y = btn_pos[1]
    }
}, 30)

function update_size() {
    if (window.innerWidth > window.innerHeight) {
        joy.parent.style.width = `${window.innerHeight / 4}px`
        joy.parent.style.height = `${window.innerHeight / 4}px`
        return
    }
    joy.parent.style.width = `${window.innerWidth / 4}px`
    joy.parent.style.height = `${window.innerWidth / 4}px`
}

update_size()
joy.resize()

addEventListener('resize', e => {
    update_size()
    joy.resize()
})

const select_bg = document.getElementById('select_bg')

let selected_bg = localStorage.getItem('bg')

if (selected_bg === null) {
    selected_bg = 'bg1.jpg'
}
else {
    select_bg.value = selected_bg
}

joy.joy.style.backgroundImage = `url('/public/imgs/${selected_bg}')`

select_bg.onchange = e => {
    selected_bg = select_bg.value
    localStorage.setItem('bg', selected_bg)
    joy.joy.style.backgroundImage = `url('/public/imgs/${selected_bg}')`
    if (select_bg.value === 'bg7.jpg') play.play()
}