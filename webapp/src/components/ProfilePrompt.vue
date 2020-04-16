<template lang="pug">
.c-profile-prompt
	.prompt-wrapper(v-scrollbar.y="")
		.prompt-wrapper-inner
			h1 Hi there!
			p Before you can join others in this awesome event, please tell us how you want to appear to other attendees.
			.profile
				.avatar
					img.gravatar-avatar(v-if="gravatarAvatarUrl", :src="gravatarAvatarUrl")
					identicon(v-else, :id="identicon || user.id", @click.native="changeIdenticon")
				bunt-input.display-name(name="displayName", label="Display name", v-model="displayName", :validation="$v.displayName")
			//- link here not strictly good UX
			a.gravatar-connected-hint(v-if="connectedGravatar", href="#", @click="connectedGravatar = false; showConnectGravatar = true") Change gravatar
			p.gravatar-hint(v-else-if="!showConnectGravatar") or connect to your #[a(href="#", @click="showConnectGravatar = true") gravatar].
			form.connect-gravatar(v-else, @submit.prevent="connectGravatar")
				bunt-input(name="gravatar", label="Gravatar email address", hint="your address is not being sent to any server", v-model="email")
				bunt-button#btn-connect-gravatar(@click="connectGravatar", :loading="searchingGravatar", :error="gravatarError") connect
			bunt-button#btn-join-world(@click="join") Join
</template>
<script>
import { mapState } from 'vuex'
import { v4 as uuid } from 'uuid'
import { required } from 'buntpapier/src/vuelidate/validators'
import Identicon from 'components/Identicon'
import { getHash, getProfile, getAvatarUrl } from 'lib/gravatar'

export default {
	components: { Identicon },
	data () {
		return {
			displayName: '',
			identicon: null,
			email: '',
			showConnectGravatar: false,
			searchingGravatar: false,
			connectedGravatar: false,
			gravatarError: null,
			gravatarAvatarUrl: null,
			gravatarHash: null
		}
	},
	validations: {
		displayName: {
			required: required('Display name cannot be empty')
		}
	},
	computed: {
		...mapState(['user'])
	},
	created () {},
	mounted () {
		this.$nextTick(() => {
		})
	},
	methods: {
		changeIdenticon () {
			this.identicon = uuid()
		},
		async connectGravatar () {
			this.searchingGravatar = true
			const hash = getHash(this.email)
			const avatarUrl = getAvatarUrl(hash, 128)
			try {
				// gravatar docs say profile only works on primary email, which I think is a lie, but let's check for an image separately anyways
				const avatarResponse = await fetch(avatarUrl)
				if (avatarResponse.status !== 200) {
					// no gravatar
					this.searchingGravatar = false
					this.gravatarError = true
					return
				}
				const profile = await getProfile(hash)
				if (profile?.entry?.length > 0) {
					console.log(profile.entry[0])
					this.gravatarHash = profile.entry[0].hash
					this.gravatarAvatarUrl = getAvatarUrl(this.gravatarHash, 128)
					this.displayName = profile.entry[0].displayName
				} else {
					this.gravatarHash = getHash(this.email)
					this.gravatarAvatarUrl = avatarUrl
				}
				this.connectedGravatar = true
			} catch (e) {
				this.gravatarError = e
			}
			this.searchingGravatar = false
		},
		join () {
			this.$v.$touch()
			if (this.$v.$invalid) return
			const profile = {
				display_name: this.displayName,
			}
			if (this.gravatarHash) {
				profile.gravatar_hash = this.gravatarHash
			} else if (this.identicon) {
				profile.identicon = this.identicon
			}
			this.$store.dispatch('updateUser', {profile})
		}
	}
}
</script>
<style lang="stylus">
.c-profile-prompt
	position: fixed
	top: 0
	left: 0
	width: 100vw
	height: 100vh
	z-index: 1000
	background-color: $clr-secondary-text-light
	display: flex
	justify-content: center
	align-items: center
	.prompt-wrapper
		card()
		display: flex
		flex-direction: column
		width: 480px
		max-height: 80vh
		.prompt-wrapper-inner
			display: flex
			flex-direction: column
			align-items: center
			padding: 32px
			h1
				margin: 0
			p
				max-width: 320px
			.profile
				margin: 16px 0 0 0
				display: flex
				align-items: center
			.avatar
				width: 128px
				height: 128px
				margin-right: 16px
			.gravatar-avatar
				height: 128px
				border-radius: 50%
			.c-identicon
				cursor: pointer
				canvas
					height: 128px
			.display-name
				width: 240px
			.gravatar-hint
				color: $clr-secondary-text-light
			.gravatar-hint, .gravatar-connected-hint
				margin-bottom: 16px
			.connect-gravatar
				display: flex
				align-items: flex-start
				margin: 16px 0 32px 0
				.bunt-input
					width: 286px
				#btn-connect-gravatar
					button-style(style: clear, color: $clr-primary)
					margin: 16px 0 0 4px
					.bunt-progress-circular svg circle
						stroke: $clr-primary
			#btn-join-world
				margin-top: 16px
				button-style(color: $clr-primary, size: large)
</style>