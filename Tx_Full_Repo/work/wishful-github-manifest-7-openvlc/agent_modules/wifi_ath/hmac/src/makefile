all: hybrid_tdma_csma_mac_x86

hybrid_tdma_csma_mac_x86:
	g++ hybrid_tdma_csma_mac.c -I /usr/include/libnl3/ -DCONFIG_LIBNL30 -o ../bin/hybrid_tdma_csma_mac -levent -lnl-genl-3 -lnl-3 -lzmq -lstdc++ -lpthread

sched:
	/lhome/zehl/OpenWRT/openwrt/staging_dir/toolchain-mips_r2_gcc-4.6-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-g++ -I/lhome/zehl/OpenWRT/openwrt/staging_dir/target-mips_r2_uClibc-0.9.33.2/usr/include/ -I/lhome/zehl/OpenWRT/openwrt/staging_dir/target-mips_r2_uClibc-0.9.33.2/usr/include/libnl-tiny/ -L/lhome/zehl/OpenWRT/openwrt/staging_dir/target-mips_r2_uClibc-0.9.33.2/usr/lib/ hybrid_tdma_csma_mac.c -o ../bin/Linux/32bit/mips/hybrid_tdma_csma_mac -levent -lm -lnl-tiny -DCONFIG_LIBNL20

clean:
	rm ../Linux/64bit/x86_64/hybrid_tdma_csma_mac
