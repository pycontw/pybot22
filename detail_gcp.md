# Run docker APPs on Pycon.tw gcp:

## Access to GCP via SSH
1. Generate the ssh keys (replace user@mail to your own)
  - $ ssh-keygen -t rsa -f ./gcp_key -C user@mail -b 2048

2. Provide  pub key ./gcp_key.pub to GCP admin (Matt) 

3. Connect to the GCP VM instance with ssh and the key (user@35.194.156.158 provided by GCP admin)
  - $ ssh -i ~/.ssh/gcp_key user@35.194.156.158


## install necessary packages on GCP VM instance
1. install git
  - $ sudo apt-get install git

2. install docker by following 

https://docs.docker.com/engine/install/debian/#install-using-the-repository

 sudo apt-get update
 sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release


sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg


echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

#sudo apt-cache madison docker-ce

3. install netcat (nc) command for mysql server socket check
  - $sudo apt-get install netcat
