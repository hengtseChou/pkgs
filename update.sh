cd $(realpath $(dirname $0))
pacman -Qqem > aur
pacman -Qqe > explicit.tmp
grep -Fxv -f base explicit.tmp > extra.tmp
grep -Fxv -f aur extra.tmp > extra
rm *.tmp
if [[ -n $(git diff) ]]; then
  if [[ $1 == "--auto" ]]; then
    git add .
    git commit -m 'auto update: pkgs changed'
    git push
  fi
fi

