# Run docker APPs on Pycon.tw gcp:

## Access to GCP via SSH
1. Generate the ssh keys (replace user@mail to your own)
  - `$ ssh-keygen -t rsa -f ./gcp_key -C user@mail -b 2048`

2. Provide  pub key ./gcp_key.pub to GCP admin (Matt) 

3. Connect to the GCP VM instance with ssh and the key (user@35.194.156.158 provided by GCP admin)
  - `$ ssh -i ~/.ssh/gcp_key user@35.194.156.158`

## install necessary packages on GCP VM instance (don't need to repeat, if already done)
1. install git if not installed, check with `git --version` (git was not installed by default)
  - `$ sudo apt-get install git`

2. install docker if not installed by following, check with `docker --version`
  - https://docs.docker.com/engine/install/debian/#install-using-the-repository

3. install netcat (nc) command for mysql server socket check, check with `docker --version`
  - `$sudo apt-get install netcat`

## git clone repo from github
1. Generate the ssh key for github.com (https method deprecate), and add the pubkey in github
  - `$ ssh-keygen -t ed25519 -C "user@mail.com"`
  - `$ cat ~/.ssh/*.pub`
  
  ssh-ed25519 XXXXC3NzaC1lZDI1NTE5XXXXIEXJmi/nOJtDHc3j+EbOvPDaVtfr1v+6u3rZK2uRDkmq user@mail.com
  -  add the pub key to https://github.com/settings/keys

  - `$ ssh -T git@github.com  #(Test the SSH connection)`
2. Clone the repo  
  - `$ git clone git@github.com:pycontw/pybot22.git`
  - `$ cd pybot22`

## update the env variables, and prepare the mysql docker
1. `$ vi env.var` and change DISCORD_TOKEN for discord bot`


## build and deploy the pybot docker
1. `$ ./deploy.sh`
