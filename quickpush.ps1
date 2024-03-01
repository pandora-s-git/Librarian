## Use : ./quickpush "push message"

param(
    [string]$message = "update (quick push)"
)

git add --all
git commit -m $message
git push