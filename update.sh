cd $(realpath $(dirname $0))
pacman -Qqm > aur
pacman -Qqe > explicit.tmp
grep -Fxv -f base explicit.tmp > extra.tmp
grep -Fxv -f aur extra.tmp > extra
rm *.tmp
