## Installation: Vagrant Setup

### Prerequisite

To get started install these softwares on your ```host``` machine:

1. Install ***Vagrant***, it is a wrapper around virtualization softwares like VirtualBox, VMWare etc.: https://www.vagrantup.com/downloads.html

2. Install ***VirtualBox***, this would be your VM provider: https://www.virtualbox.org/wiki/Downloads

3. Install ***Git***, it is a distributed version control system: https://git-scm.com/downloads

4. Install X Server and SSH capable terminal
    * For Windows install [Xming](http://sourceforge.net/project/downloading.php?group_id=156984&filename=Xming-6-9-0-31-setup.exe) and [Putty](http://the.earth.li/~sgtatham/putty/latest/x86/putty.exe).
    * For MAC OS install [XQuartz](http://xquartz.macosforge.org/trac/wiki) and Terminal.app (builtin)
    * Linux comes pre-installed with X server and Gnome terminal + SSH (buitlin)   

### Getting Started

Clone the ```Sonata``` repository from Github:
```bash 
$ git clone https://github.com/Sonata-Princeton/SONATA-DEV.git
```

Change the directory to ```Sonata```:
```bash
$ cd SONATA-DEV
```

Checkout the `tutorial` branch:
```bash
$ git checkout tutorial
```

Now run the vagrant up command. This will read the Vagrantfile from the current directory and provision the VM accordingly:
```bash
$ vagrant up
```

Vagrant 

The provisioning scripts will install all the required software (and their dependencies) to run the `Sonata` demo. Now ssh in to the VM:
```bash
$ vagrant ssh
```

Notes:
* Notice that the 
[line](https://github.com/Sonata-Princeton/SONATA-DEV/blob/tutorial/Vagrantfile#L52)
in the Vagrant file ensures that the files in your `SONATA-DEV` directory 
are in sync with the ones in the `/home/vagrant/dev` directory of your VM. 
This ensures that you can use any IDEs (editors) in your host 
machine for development. If you prefer to edit files in the VM directly, 
feel free to install any software using the `APT` software user interface. 
For example, to install `vim` editor, you need to run the command:
```bash
$ sudo apt-get install vim
```
