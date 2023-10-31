#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x2cce4d13, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0x57d5dab0, __VMLINUX_SYMBOL_STR(usb_register_driver) },
	{ 0x58ec970f, __VMLINUX_SYMBOL_STR(__napi_schedule) },
	{ 0x85df9b6c, __VMLINUX_SYMBOL_STR(strsep) },
	{ 0x1d59f781, __VMLINUX_SYMBOL_STR(eth_type_trans) },
	{ 0x56c54bc3, __VMLINUX_SYMBOL_STR(napi_gro_receive) },
	{ 0xef7ce5fe, __VMLINUX_SYMBOL_STR(single_release) },
	{ 0xe707d823, __VMLINUX_SYMBOL_STR(__aeabi_uidiv) },
	{ 0xdb7305a1, __VMLINUX_SYMBOL_STR(__stack_chk_fail) },
	{ 0xd2da1048, __VMLINUX_SYMBOL_STR(register_netdevice_notifier) },
	{ 0x97255bdf, __VMLINUX_SYMBOL_STR(strlen) },
	{ 0x7d77443f, __VMLINUX_SYMBOL_STR(skb_queue_tail) },
	{ 0x20000329, __VMLINUX_SYMBOL_STR(simple_strtoul) },
	{ 0x43a09d15, __VMLINUX_SYMBOL_STR(cfg80211_mgmt_tx_status) },
	{ 0x9d669763, __VMLINUX_SYMBOL_STR(memcpy) },
	{ 0x1fe7d4c8, __VMLINUX_SYMBOL_STR(proc_mkdir_data) },
	{ 0x5e10cb4, __VMLINUX_SYMBOL_STR(dev_get_by_name) },
	{ 0x4b298ca7, __VMLINUX_SYMBOL_STR(wiphy_apply_custom_regulatory) },
	{ 0x91715312, __VMLINUX_SYMBOL_STR(sprintf) },
	{ 0x9c64fbd, __VMLINUX_SYMBOL_STR(ieee80211_frequency_to_channel) },
	{ 0x7dff118, __VMLINUX_SYMBOL_STR(cfg80211_rx_mgmt) },
	{ 0x343a1a8, __VMLINUX_SYMBOL_STR(__list_add) },
	{ 0xb7a4ef91, __VMLINUX_SYMBOL_STR(napi_disable) },
	{ 0x28f77f54, __VMLINUX_SYMBOL_STR(free_netdev) },
	{ 0x980af7d, __VMLINUX_SYMBOL_STR(__cfg80211_alloc_reply_skb) },
	{ 0x44da5d0f, __VMLINUX_SYMBOL_STR(__csum_ipv6_magic) },
	{ 0xd75580ff, __VMLINUX_SYMBOL_STR(unregister_netdevice_queue) },
	{ 0x76e25e63, __VMLINUX_SYMBOL_STR(usb_submit_urb) },
	{ 0x2196324, __VMLINUX_SYMBOL_STR(__aeabi_idiv) },
	{ 0x3780dfbe, __VMLINUX_SYMBOL_STR(netif_receive_skb) },
	{ 0x760a0f4f, __VMLINUX_SYMBOL_STR(yield) },
	{ 0xe4689576, __VMLINUX_SYMBOL_STR(ktime_get_with_offset) },
	{ 0xf4fd3fc, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0x60352082, __VMLINUX_SYMBOL_STR(register_inet6addr_notifier) },
	{ 0xb8972fee, __VMLINUX_SYMBOL_STR(alloc_etherdev_mqs) },
	{ 0x2e31179d, __VMLINUX_SYMBOL_STR(usb_free_urb) },
	{ 0xb35361bf, __VMLINUX_SYMBOL_STR(cfg80211_new_sta) },
	{ 0xf8d1965a, __VMLINUX_SYMBOL_STR(unregister_netdev) },
	{ 0xf9a482f9, __VMLINUX_SYMBOL_STR(msleep) },
	{ 0xbedb8415, __VMLINUX_SYMBOL_STR(flush_signals) },
	{ 0x9d0d6206, __VMLINUX_SYMBOL_STR(unregister_netdevice_notifier) },
	{ 0x29f7fe79, __VMLINUX_SYMBOL_STR(cfg80211_inform_bss_frame_data) },
	{ 0x317b980a, __VMLINUX_SYMBOL_STR(cfg80211_connect_result) },
	{ 0x8e865d3c, __VMLINUX_SYMBOL_STR(arm_delay_ops) },
	{ 0x28cc25db, __VMLINUX_SYMBOL_STR(arm_copy_from_user) },
	{ 0x76ac3c06, __VMLINUX_SYMBOL_STR(wait_for_completion) },
	{ 0xc058df80, __VMLINUX_SYMBOL_STR(dev_alloc_name) },
	{ 0x16305289, __VMLINUX_SYMBOL_STR(warn_slowpath_null) },
	{ 0xae7baa31, __VMLINUX_SYMBOL_STR(usb_kill_urb) },
	{ 0x598542b2, __VMLINUX_SYMBOL_STR(_raw_spin_lock_irqsave) },
	{ 0xb35ee906, __VMLINUX_SYMBOL_STR(netif_carrier_on) },
	{ 0x30ed0f84, __VMLINUX_SYMBOL_STR(cfg80211_unlink_bss) },
	{ 0x65e75cb6, __VMLINUX_SYMBOL_STR(__list_del_entry) },
	{ 0x4605c027, __VMLINUX_SYMBOL_STR(__dev_kfree_skb_any) },
	{ 0x7564c25e, __VMLINUX_SYMBOL_STR(proc_create_data) },
	{ 0xbd0a5062, __VMLINUX_SYMBOL_STR(find_vpid) },
	{ 0x50ea67c1, __VMLINUX_SYMBOL_STR(usb_alloc_coherent) },
	{ 0x1000e51, __VMLINUX_SYMBOL_STR(schedule) },
	{ 0x20bf2e6f, __VMLINUX_SYMBOL_STR(skb_push) },
	{ 0xa46f2405, __VMLINUX_SYMBOL_STR(wait_for_completion_timeout) },
	{ 0xf1969a8e, __VMLINUX_SYMBOL_STR(__usecs_to_jiffies) },
	{ 0xf4fa543b, __VMLINUX_SYMBOL_STR(arm_copy_to_user) },
	{ 0x6df1aaf1, __VMLINUX_SYMBOL_STR(kernel_sigaction) },
	{ 0x550e25c0, __VMLINUX_SYMBOL_STR(kill_pid) },
	{ 0xbf38f273, __VMLINUX_SYMBOL_STR(skb_trim) },
	{ 0x706d051c, __VMLINUX_SYMBOL_STR(del_timer_sync) },
	{ 0xa1d55e90, __VMLINUX_SYMBOL_STR(_raw_spin_lock_bh) },
	{ 0xeebab20f, __VMLINUX_SYMBOL_STR(netif_napi_add) },
	{ 0x4be7fb63, __VMLINUX_SYMBOL_STR(up) },
	{ 0xfe029963, __VMLINUX_SYMBOL_STR(unregister_inetaddr_notifier) },
	{ 0x2a3aa678, __VMLINUX_SYMBOL_STR(_test_and_clear_bit) },
	{ 0xf808c4bc, __VMLINUX_SYMBOL_STR(register_netdev) },
	{ 0x10dfde67, __VMLINUX_SYMBOL_STR(cfg80211_put_bss) },
	{ 0x40a4a924, __VMLINUX_SYMBOL_STR(cfg80211_roamed) },
	{ 0xf68285c0, __VMLINUX_SYMBOL_STR(register_inetaddr_notifier) },
	{ 0x35a8e772, __VMLINUX_SYMBOL_STR(remove_proc_entry) },
	{ 0x7d11c268, __VMLINUX_SYMBOL_STR(jiffies) },
	{ 0x646aa0eb, __VMLINUX_SYMBOL_STR(cfg80211_scan_done) },
	{ 0x40c01c2f, __VMLINUX_SYMBOL_STR(__init_swait_queue_head) },
	{ 0xb3f7646e, __VMLINUX_SYMBOL_STR(kthread_should_stop) },
	{ 0x5136d7f4, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0x2102eced, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0xd62c833f, __VMLINUX_SYMBOL_STR(schedule_timeout) },
	{ 0xab9c8455, __VMLINUX_SYMBOL_STR(napi_complete_done) },
	{ 0xa22d16a3, __VMLINUX_SYMBOL_STR(seq_read) },
	{ 0xa0135f47, __VMLINUX_SYMBOL_STR(mutex_lock_interruptible) },
	{ 0x4d8afd2f, __VMLINUX_SYMBOL_STR(netif_carrier_off) },
	{ 0xff178f6, __VMLINUX_SYMBOL_STR(__aeabi_idivmod) },
	{ 0xf4c91ed, __VMLINUX_SYMBOL_STR(ns_to_timespec) },
	{ 0x1dfcac9a, __VMLINUX_SYMBOL_STR(usb_get_dev) },
	{ 0xd36ea1cf, __VMLINUX_SYMBOL_STR(param_ops_uint) },
	{ 0xc890baa4, __VMLINUX_SYMBOL_STR(kthread_create_on_node) },
	{ 0xcfde9e10, __VMLINUX_SYMBOL_STR(__vfs_read) },
	{ 0x676bbc0f, __VMLINUX_SYMBOL_STR(_set_bit) },
	{ 0x49ebacbd, __VMLINUX_SYMBOL_STR(_clear_bit) },
	{ 0xb0b154c2, __VMLINUX_SYMBOL_STR(wake_up_process) },
	{ 0xb681e4d8, __VMLINUX_SYMBOL_STR(register_netdevice) },
	{ 0xe59174b1, __VMLINUX_SYMBOL_STR(seq_lseek) },
	{ 0x86935d24, __VMLINUX_SYMBOL_STR(PDE_DATA) },
	{ 0xbe003248, __VMLINUX_SYMBOL_STR(skb_copy) },
	{ 0xecde8743, __VMLINUX_SYMBOL_STR(param_ops_charp) },
	{ 0x8f678b07, __VMLINUX_SYMBOL_STR(__stack_chk_guard) },
	{ 0x16e5c2a, __VMLINUX_SYMBOL_STR(mod_timer) },
	{ 0x8ae3240e, __VMLINUX_SYMBOL_STR(skb_copy_bits) },
	{ 0x328a05f1, __VMLINUX_SYMBOL_STR(strncpy) },
	{ 0x2422969b, __VMLINUX_SYMBOL_STR(cfg80211_ibss_joined) },
	{ 0x87c29eab, __VMLINUX_SYMBOL_STR(netif_rx) },
	{ 0x82072614, __VMLINUX_SYMBOL_STR(tasklet_kill) },
	{ 0x9cd2ace1, __VMLINUX_SYMBOL_STR(usb_deregister) },
	{ 0x9dbab6f3, __VMLINUX_SYMBOL_STR(skb_dequeue) },
	{ 0x34268454, __VMLINUX_SYMBOL_STR(cfg80211_michael_mic_failure) },
	{ 0xf8f58676, __VMLINUX_SYMBOL_STR(netif_tx_wake_queue) },
	{ 0xebdae34b, __VMLINUX_SYMBOL_STR(complete_and_exit) },
	{ 0x13b83b3f, __VMLINUX_SYMBOL_STR(cfg80211_disconnected) },
	{ 0x607b8a4e, __VMLINUX_SYMBOL_STR(kthread_stop) },
	{ 0xa735db59, __VMLINUX_SYMBOL_STR(prandom_u32) },
	{ 0x47939e0d, __VMLINUX_SYMBOL_STR(__tasklet_hi_schedule) },
	{ 0x9a1dfd65, __VMLINUX_SYMBOL_STR(strpbrk) },
	{ 0xf3627fe5, __VMLINUX_SYMBOL_STR(init_net) },
	{ 0x78181925, __VMLINUX_SYMBOL_STR(__cfg80211_send_event_skb) },
	{ 0x2aa0e4fc, __VMLINUX_SYMBOL_STR(strncasecmp) },
	{ 0x349cba85, __VMLINUX_SYMBOL_STR(strchr) },
	{ 0x37a0cba, __VMLINUX_SYMBOL_STR(kfree) },
	{ 0x48ad8019, __VMLINUX_SYMBOL_STR(seq_printf) },
	{ 0xc66e75bb, __VMLINUX_SYMBOL_STR(complete) },
	{ 0xd6dff031, __VMLINUX_SYMBOL_STR(cfg80211_get_bss) },
	{ 0x21ce674f, __VMLINUX_SYMBOL_STR(wiphy_new_nm) },
	{ 0x912df412, __VMLINUX_SYMBOL_STR(param_array_ops) },
	{ 0x34f58c2b, __VMLINUX_SYMBOL_STR(wiphy_free) },
	{ 0xaba38fa8, __VMLINUX_SYMBOL_STR(device_init_wakeup) },
	{ 0xdd3916ac, __VMLINUX_SYMBOL_STR(_raw_spin_unlock_bh) },
	{ 0xf7802486, __VMLINUX_SYMBOL_STR(__aeabi_uidivmod) },
	{ 0x80d8d77c, __VMLINUX_SYMBOL_STR(seq_open) },
	{ 0x1afae5e7, __VMLINUX_SYMBOL_STR(down_interruptible) },
	{ 0x2e5810c6, __VMLINUX_SYMBOL_STR(__aeabi_unwind_cpp_pr1) },
	{ 0xd93a9121, __VMLINUX_SYMBOL_STR(proc_get_parent_data) },
	{ 0xb40eb3c3, __VMLINUX_SYMBOL_STR(skb_put) },
	{ 0xf1a8b445, __VMLINUX_SYMBOL_STR(__ieee80211_get_channel) },
	{ 0xe113bbbc, __VMLINUX_SYMBOL_STR(csum_partial) },
	{ 0x530dbc16, __VMLINUX_SYMBOL_STR(cfg80211_ready_on_channel) },
	{ 0x12a38747, __VMLINUX_SYMBOL_STR(usleep_range) },
	{ 0xe914e41e, __VMLINUX_SYMBOL_STR(strcpy) },
	{ 0x7f02188f, __VMLINUX_SYMBOL_STR(__msecs_to_jiffies) },
	{ 0x59e5070d, __VMLINUX_SYMBOL_STR(__do_div64) },
	{ 0x62ffece6, __VMLINUX_SYMBOL_STR(skb_clone) },
	{ 0x84b183ae, __VMLINUX_SYMBOL_STR(strncmp) },
	{ 0xfa2a45e, __VMLINUX_SYMBOL_STR(__memzero) },
	{ 0xb04c693b, __VMLINUX_SYMBOL_STR(usb_put_dev) },
	{ 0x10708128, __VMLINUX_SYMBOL_STR(filp_close) },
	{ 0x51d559d1, __VMLINUX_SYMBOL_STR(_raw_spin_unlock_irqrestore) },
	{ 0x99bb8806, __VMLINUX_SYMBOL_STR(memmove) },
	{ 0xca54fee, __VMLINUX_SYMBOL_STR(_test_and_set_bit) },
	{ 0x56403888, __VMLINUX_SYMBOL_STR(cfg80211_ch_switch_notify) },
	{ 0x36c2a73, __VMLINUX_SYMBOL_STR(netif_wake_subqueue) },
	{ 0xb1ad28e0, __VMLINUX_SYMBOL_STR(__gnu_mcount_nc) },
	{ 0x1719bb73, __VMLINUX_SYMBOL_STR(usb_control_msg) },
	{ 0x7494d5f5, __VMLINUX_SYMBOL_STR(param_ops_int) },
	{ 0x9580deb, __VMLINUX_SYMBOL_STR(init_timer_key) },
	{ 0x12da5bb2, __VMLINUX_SYMBOL_STR(__kmalloc) },
	{ 0x8293d54b, __VMLINUX_SYMBOL_STR(single_open) },
	{ 0x5f754e5a, __VMLINUX_SYMBOL_STR(memset) },
	{ 0x2b0a5db3, __VMLINUX_SYMBOL_STR(__pskb_pull_tail) },
	{ 0x9c0bd51f, __VMLINUX_SYMBOL_STR(_raw_spin_lock) },
	{ 0xbaac5ef8, __VMLINUX_SYMBOL_STR(usb_alloc_urb) },
	{ 0xe2d5255a, __VMLINUX_SYMBOL_STR(strcmp) },
	{ 0xc698b56, __VMLINUX_SYMBOL_STR(usb_reset_device) },
	{ 0x37befc70, __VMLINUX_SYMBOL_STR(jiffies_to_msecs) },
	{ 0x68868cc1, __VMLINUX_SYMBOL_STR(filp_open) },
	{ 0xad574628, __VMLINUX_SYMBOL_STR(usb_autopm_get_interface) },
	{ 0xb81960ca, __VMLINUX_SYMBOL_STR(snprintf) },
	{ 0x63cc666d, __VMLINUX_SYMBOL_STR(wiphy_unregister) },
	{ 0x1f533f3f, __VMLINUX_SYMBOL_STR(seq_release) },
	{ 0xea646b13, __VMLINUX_SYMBOL_STR(netif_tx_stop_all_queues) },
	{ 0x3b935766, __VMLINUX_SYMBOL_STR(cfg80211_del_sta_sinfo) },
	{ 0x9545af6d, __VMLINUX_SYMBOL_STR(tasklet_init) },
	{ 0x4fbe5807, __VMLINUX_SYMBOL_STR(cfg80211_vendor_cmd_reply) },
	{ 0xfaef0ed, __VMLINUX_SYMBOL_STR(__tasklet_schedule) },
	{ 0x20c55ae0, __VMLINUX_SYMBOL_STR(sscanf) },
	{ 0xf55ac006, __VMLINUX_SYMBOL_STR(__netdev_alloc_skb) },
	{ 0x27e1a049, __VMLINUX_SYMBOL_STR(printk) },
	{ 0x65c7184, __VMLINUX_SYMBOL_STR(nla_put_nohdr) },
	{ 0xd6ee688f, __VMLINUX_SYMBOL_STR(vmalloc) },
	{ 0x443aa2d, __VMLINUX_SYMBOL_STR(cfg80211_remain_on_channel_expired) },
	{ 0xd845cf95, __VMLINUX_SYMBOL_STR(nla_put) },
	{ 0x9338d3a4, __VMLINUX_SYMBOL_STR(wiphy_register) },
	{ 0x3820326, __VMLINUX_SYMBOL_STR(__cfg80211_alloc_event_skb) },
	{ 0x999e8297, __VMLINUX_SYMBOL_STR(vfree) },
	{ 0x6b07ca61, __VMLINUX_SYMBOL_STR(netif_napi_del) },
	{ 0x71c90087, __VMLINUX_SYMBOL_STR(memcmp) },
	{ 0x2fe252cc, __VMLINUX_SYMBOL_STR(unregister_inet6addr_notifier) },
	{ 0x26bb11af, __VMLINUX_SYMBOL_STR(usb_free_coherent) },
	{ 0x85670f1d, __VMLINUX_SYMBOL_STR(rtnl_is_locked) },
	{ 0x3f591ec3, __VMLINUX_SYMBOL_STR(skb_pull) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=cfg80211";

MODULE_ALIAS("usb:v0BDAp8179d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0BDAp0179d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v07B8p8179d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0BDAp8179d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v2357p010Cd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0DF6p0076d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v2001p330Fd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v2001p3310d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v2001p3311d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v2001p331Bd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v056Ep4008d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v7392pB811d*dc*dsc*dp*ic*isc*ip*in*");

MODULE_INFO(srcversion, "A5F98BB1793976C6FFC813F");
