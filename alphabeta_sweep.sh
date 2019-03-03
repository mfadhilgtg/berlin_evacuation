#! /bin/bash
clear
#parameter
# $1 = epos_directory


#epos_directory=../../EPOS/release-0.0.1/release-0.0.1
epos_directory=$1

#Dataset is located in the EPOS folder and epos_properties has been set

alpha=0
beta=0

until [ $beta -eq 11 ]; do
	echo "Running simulation beta=" $beta "alpha=" $alpha
	sed -i "s/\("beta" *= *\).*/\1"0."$beta/" $epos_directory/conf/epos.properties
	sed -i "s/\("alpha" *= *\).*/\1"0."$alpha/" $epos_directory/conf/epos.properties
	if [ $beta -eq 10 ]; then
		sed -i "s/\("beta" *= *\).*/\1""1/" $epos_directory/conf/epos.properties
	fi
	echo "Running IEPOS"
	cd $epos_directory
	java -jar epos-tutorial.jar
	cd -
	cd $epos_directory/output
	eval beta$beta=$epos_directory/output/$(\ls -1dt */ | head -n 1)	
	cd -
	let beta+=1
	#alpha=0
done

alpha=0
beta=0

until [ $alpha -eq 11 ]; do
	echo "Running simulation beta=" $beta "alpha=" $alpha
	sed -i "s/\("beta" *= *\).*/\1"0."$beta/" $epos_directory/conf/epos.properties
	sed -i "s/\("alpha" *= *\).*/\1"0."$alpha/" $epos_directory/conf/epos.properties
	if [ $alpha -eq 10 ]; then
		sed -i "s/\("alpha" *= *\).*/\1""1/" $epos_directory/conf/epos.properties
	fi
	echo "Running IEPOS"
	cd $epos_directory
	java -jar epos-tutorial.jar
	cd -
	cd $epos_directory/output
	eval alpha$alpha=$epos_directory/output/$(\ls -1dt */ | head -n 1)	
	cd -
	
	let alpha+=1
	#alpha=0
done

python plot_tradeoff.py --var0 $beta0  --var1 $beta1 --var2 $beta2 --var3 $beta3 --var4 $beta4 --var5 $beta5 --var6 $beta6 --var7 $beta7 --var8 $beta8 --var9 $beta9 --var10 $beta10 --variable 1

python plot_tradeoff.py --var0 $alpha0  --var1 $alpha1 --var2 $alpha2 --var3 $alpha3 --var4 $alpha4 --var5 $alpha5 --var6 $alpha6 --var7 $alpha7 --var8 $alpha8 --var9 $alpha9 --var10 $alpha10 --variable 0
