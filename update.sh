cd $(realpath $(dirname $0))
pacman -Qqm > aur.txt
pacman -Qqe > explicit.tmp
grep -Fxv -f base.txt explicit.tmp > extra.tmp
grep -Fxv -f aur.txt extra.tmp > extra.txt
rm *.tmp
