new Vue({
	el: '#app',
	delimiters: ['[[', ']]'],
	data: {
		url: '',
		resolution: '1280x720',
		bitrate: '1000k',
		fps: 30,
		streams: {}
	},
	methods: {
		startStream() {
			fetch('/start_stream', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					url: this.url,
					resolution: this.resolution,
					bitrate: this.bitrate,
					fps: this.fps
				}),
			})
				.then(response => response.json())
				.then(data => {
					this.streams[data.id] = data.data
					this.url = ''
				})
		},
		stopStream(id) {
			fetch(`/stop_stream/${id}`, { method: 'POST' })
				.then(response => response.json())
				.then(data => {
					if (data.success) {
						Vue.delete(this.streams, id)
					}
				})
		},
		loadStreams() {
			fetch('/streams')
				.then(response => response.json())
				.then(data => {
					this.streams = data
				})
		}
	},
	mounted() {
		this.loadStreams()
		setInterval(this.loadStreams, 5000)
	}
})
